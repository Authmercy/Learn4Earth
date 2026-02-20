# EcoLearn AI - Architecture Base de Donnees MySQL NDB Cluster

**Version** : 1.4.0
**Date** : 11/02/2026
**Moteur** : MySQL NDB Cluster 8.0 + Redis 7.2 + Prometheus + Grafana

---

## Table des matieres

1. [Vue d'ensemble du cluster](#1-vue-densemble-du-cluster)
2. [Topologie des noeuds](#2-topologie-des-noeuds)
3. [Configuration des noeuds](#3-configuration-des-noeuds)
4. [Schema de la base de donnees](#4-schema-de-la-base-de-donnees)
5. [Scripts SQL de creation](#5-scripts-sql-de-creation)
6. [Index et optimisation](#6-index-et-optimisation)
7. [Replication et haute disponibilite](#7-replication-et-haute-disponibilite)
8. [Backup et restauration](#8-backup-et-restauration)
9. [Monitoring et maintenance](#9-monitoring-et-maintenance)
10. [Connexion depuis le backend FastAPI](#10-connexion-depuis-le-backend-fastapi)
11. [Redis - Cache et Rate Limiting](#11-redis---cache-et-rate-limiting)
12. [Stack de Monitoring (Prometheus + Grafana)](#12-stack-de-monitoring-prometheus--grafana)
13. [Cron Backup - Replication automatique](#13-cron-backup---replication-automatique)
14. [Endpoints API de monitoring](#14-endpoints-api-de-monitoring)

---

## 1. Vue d'ensemble du cluster

### Architecture MySQL NDB Cluster (4 noeuds)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MYSQL NDB CLUSTER - ECOLEARNAI                           │
│                    Haute disponibilite + Partitionnement                    │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────┐
                    │      BACKEND FASTAPI         │
                    │   (206.189.56.166:8000)       │
                    │                              │
                    │   SQLAlchemy + PyMySQL        │
                    │   pool_pre_ping=True          │
                    │   pool_recycle=3600           │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────▼───────────────────┐
                    │     LOAD BALANCER MySQL       │
                    │     (ProxySQL ou HAProxy)     │
                    │     Port: 6033               │
                    │                              │
                    │  Read/Write splitting        │
                    │  Health checks               │
                    │  Connection pooling           │
                    └───────┬──────────┬───────────┘
                            │          │
              ┌─────────────┘          └─────────────┐
              │                                      │
    ┌─────────▼──────────┐            ┌──────────────▼─────────┐
    │   SQL NODE #1      │            │     SQL NODE #2        │
    │   (mysqld + ndbapi)│            │     (mysqld + ndbapi)  │
    │                    │            │                        │
    │  IP: 159.89.13.54  │            │  IP: 159.89.13.55     │
    │  Port: 3306        │            │  Port: 3306            │
    │                    │            │                        │
    │  Role: Read/Write  │            │  Role: Read/Write      │
    │  (Active-Active)   │            │  (Active-Active)       │
    └────────┬───────────┘            └──────────┬─────────────┘
             │                                   │
             │        NDB Protocol (TCP)         │
             │                                   │
    ┌────────▼───────────────────────────────────▼─────────────┐
    │                                                          │
    │              RESEAU INTERNE CLUSTER (VLAN)               │
    │              (Communication inter-noeuds)                │
    │                                                          │
    └──┬──────────┬──────────────────┬──────────┬─────────────┘
       │          │                  │          │
  ┌────▼────┐ ┌───▼─────┐     ┌─────▼───┐ ┌───▼─────┐
  │ MGMT    │ │ MGMT    │     │ DATA    │ │ DATA    │
  │ NODE #1 │ │ NODE #2 │     │ NODE #1 │ │ DATA    │
  │ (ndb_   │ │ (ndb_   │     │ (ndbd)  │ │ NODE #2 │
  │  mgmd)  │ │  mgmd)  │     │         │ │ (ndbd)  │
  │         │ │         │     │         │ │         │
  │ PRIMAIRE│ │ SECONDR │     │ NodeGrp │ │ NodeGrp │
  │         │ │ (failovr│)    │   0     │ │   0     │
  │IP: .56  │ │IP: .57  │     │         │ │         │
  │Port:1186│ │Port:1186│     │IP: .58  │ │IP: .59  │
  └─────────┘ └─────────┘     │Port:2202│ │Port:2202│
                               │         │ │         │
                               │ Replica │ │ Replica │
                               │ #1      │ │ #2      │
                               └─────────┘ └─────────┘
```

### Principe de fonctionnement

```
┌──────────────────────────────────────────────────────────────────┐
│                   COMMENT CA MARCHE                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Les MANAGEMENT NODES (ndb_mgmd) :                           │
│     - Gerent la configuration du cluster                         │
│     - Surveillent l'etat de tous les noeuds                     │
│     - Coordonnent le demarrage et l'arret                       │
│     - 2 noeuds = basculement automatique si le primaire tombe   │
│                                                                  │
│  2. Les DATA NODES (ndbd) :                                     │
│     - Stockent les donnees en memoire (RAM) + disque            │
│     - Chaque donnee est repliquee sur les 2 noeuds              │
│     - Si un noeud tombe, l'autre sert les donnees               │
│     - Partitionnement automatique (sharding)                    │
│                                                                  │
│  3. Les SQL NODES (mysqld) :                                    │
│     - Interface SQL standard (compatible MySQL 8.0)              │
│     - Le backend FastAPI se connecte a ces noeuds               │
│     - 2 noeuds = repartition de charge + failover               │
│     - Fonctionnent en mode Active-Active                        │
│                                                                  │
│  TOTAL : 6 processus sur 4-6 serveurs                           │
│  - 2 x ndb_mgmd (management)                                   │
│  - 2 x ndbd (stockage/data)                                    │
│  - 2 x mysqld (SQL/acces)                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Topologie des noeuds

### Allocation des serveurs

| Serveur | IP | Noeuds | RAM | Disque | CPU | Role |
|---------|-----|--------|-----|--------|-----|------|
| srv-mgmt-1 | 159.89.13.56 | ndb_mgmd #1 (NodeId=1) | 2 Go | 20 Go SSD | 2 vCPU | Management primaire |
| srv-mgmt-2 | 159.89.13.57 | ndb_mgmd #2 (NodeId=2) | 2 Go | 20 Go SSD | 2 vCPU | Management secondaire |
| srv-data-1 | 159.89.13.58 | ndbd #1 (NodeId=3) | 8 Go | 100 Go SSD | 4 vCPU | Stockage replica #1 |
| srv-data-2 | 159.89.13.59 | ndbd #2 (NodeId=4) | 8 Go | 100 Go SSD | 4 vCPU | Stockage replica #2 |
| srv-sql-1 | 159.89.13.54 | mysqld #1 (NodeId=5) | 4 Go | 50 Go SSD | 2 vCPU | SQL node (actuel) |
| srv-sql-2 | 159.89.13.55 | mysqld #2 (NodeId=6) | 4 Go | 50 Go SSD | 2 vCPU | SQL node (nouveau) |

### Diagramme reseau

```
                        INTERNET
                           │
                    ┌──────▼──────┐
                    │  Firewall   │
                    │  (iptables) │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │      RESEAU PUBLIC          │
            │      159.89.13.0/24         │
            │                              │
            │  ┌────────┐  ┌────────┐     │
            │  │SQL #1  │  │SQL #2  │     │
            │  │ .54    │  │ .55    │     │ ← Backend se connecte ici
            │  │ :3306  │  │ :3306  │     │
            │  └───┬────┘  └───┬────┘     │
            │      │           │          │
            └──────┼───────────┼──────────┘
                   │           │
            ┌──────┼───────────┼──────────┐
            │      │  RESEAU PRIVE        │
            │      │  10.0.0.0/24         │
            │      │  (VLAN cluster)      │
            │      │           │          │
            │  ┌───▼────┐  ┌──▼─────┐    │
            │  │MGMT #1 │  │MGMT #2 │    │
            │  │10.0.0.1│  │10.0.0.2│    │
            │  │ :1186  │  │ :1186  │    │
            │  └───┬────┘  └───┬────┘    │
            │      │           │          │
            │  ┌───▼────┐  ┌──▼─────┐    │
            │  │DATA #1 │  │DATA #2 │    │
            │  │10.0.0.3│  │10.0.0.4│    │
            │  │ :2202  │  │ :2202  │    │
            │  └────────┘  └────────┘    │
            │                             │
            └─────────────────────────────┘
```

---

## 3. Configuration des noeuds

### 3.1 Configuration du cluster (`config.ini`)

Ce fichier est place sur les **noeuds de management** dans `/var/lib/mysql-cluster/config.ini`.

```ini
# ================================================================
# MySQL NDB Cluster - Configuration EcoLearn AI
# Fichier : /var/lib/mysql-cluster/config.ini
# Placement : sur les 2 noeuds management (ndb_mgmd)
# ================================================================

[ndbd default]
# Nombre de replicas (chaque donnee est copiee sur 2 noeuds)
NoOfReplicas=2

# Memoire allouee pour les donnees (ajuster selon la charge)
DataMemory=4096M          # 4 Go pour les donnees
IndexMemory=512M          # 512 Mo pour les index

# Fichiers de donnees sur disque (backup memoire)
FileSystemPath=/var/lib/mysql-cluster/data

# Parametres de performance
MaxNoOfConcurrentOperations=100000
MaxNoOfConcurrentTransactions=16384
MaxNoOfOrderedIndexes=512
MaxNoOfUniqueHashIndexes=256

# Timeout et heartbeat
HeartbeatIntervalDbDb=5000        # Heartbeat entre data nodes (5s)
HeartbeatIntervalDbApi=5000       # Heartbeat vers SQL nodes (5s)
TransactionDeadlockDetectionTimeout=5000

# Redo log (pour recovery)
FragmentLogFileSize=256M
NoOfFragmentLogFiles=16
RedoBuffer=64M

# Checkpoints (sauvegarde periodique sur disque)
TimeBetweenLocalCheckpoints=20    # Checkpoint local toutes les ~20s
TimeBetweenGlobalCheckpoints=2000 # Checkpoint global toutes les 2s
DiskCheckpointSpeed=10M
DiskCheckpointSpeedInRestart=100M

# Compression
CompressedLCP=1                   # Compresser les checkpoints locaux
CompressedBackup=1                # Compresser les backups

[ndb_mgmd default]
DataDir=/var/lib/mysql-cluster/mgmt

# ────────────────────────────────────────────────
# MANAGEMENT NODE #1 (Primaire)
# ────────────────────────────────────────────────
[ndb_mgmd]
NodeId=1
HostName=159.89.13.56
DataDir=/var/lib/mysql-cluster/mgmt
PortNumber=1186
# ArbitrationRank : 1 = primaire pour l'arbitrage
ArbitrationRank=1

# ────────────────────────────────────────────────
# MANAGEMENT NODE #2 (Secondaire / Failover)
# ────────────────────────────────────────────────
[ndb_mgmd]
NodeId=2
HostName=159.89.13.57
DataDir=/var/lib/mysql-cluster/mgmt
PortNumber=1186
ArbitrationRank=2

# ────────────────────────────────────────────────
# DATA NODE #1 (Stockage - Replica #1)
# ────────────────────────────────────────────────
[ndbd]
NodeId=3
HostName=159.89.13.58
DataDir=/var/lib/mysql-cluster/data
# NodeGroup est attribue automatiquement (NodeGroup=0)

# ────────────────────────────────────────────────
# DATA NODE #2 (Stockage - Replica #2)
# ────────────────────────────────────────────────
[ndbd]
NodeId=4
HostName=159.89.13.59
DataDir=/var/lib/mysql-cluster/data

# ────────────────────────────────────────────────
# SQL NODE #1 (API mysqld)
# ────────────────────────────────────────────────
[mysqld]
NodeId=5
HostName=159.89.13.54

# ────────────────────────────────────────────────
# SQL NODE #2 (API mysqld)
# ────────────────────────────────────────────────
[mysqld]
NodeId=6
HostName=159.89.13.55

# ────────────────────────────────────────────────
# Connexions TCP internes
# ────────────────────────────────────────────────
[tcp default]
SendBufferMemory=4M
ReceiveBufferMemory=4M
```

### 3.2 Configuration MySQL (`my.cnf`) pour les SQL Nodes

Ce fichier est place sur les **noeuds SQL** (`srv-sql-1` et `srv-sql-2`).

```ini
# ================================================================
# MySQL NDB Cluster - Configuration SQL Node
# Fichier : /etc/mysql/my.cnf (sur srv-sql-1 et srv-sql-2)
# ================================================================

[mysqld]
# ── Connexion au cluster NDB ──
ndbcluster
ndb-connectstring=159.89.13.56:1186,159.89.13.57:1186

# ── Moteur de stockage par defaut ──
default_storage_engine=NDBCLUSTER

# ── Reseau ──
bind-address=0.0.0.0
port=3306

# ── Base de donnees ──
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock

# ── Charset (compatible avec l'application) ──
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# ── Connexions ──
max_connections=500
wait_timeout=28800
interactive_timeout=28800

# ── Cache et buffers ──
innodb_buffer_pool_size=1G
query_cache_size=0              # Desactive (NDB gere son propre cache)
tmp_table_size=64M
max_heap_table_size=64M

# ── Logs ──
log_error=/var/log/mysql/error.log
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
long_query_time=2

# ── Securite ──
skip-name-resolve                # Pas de resolution DNS
local-infile=0                   # Desactiver LOAD DATA LOCAL

# ── NDB specifique ──
ndb_log_bin=ON                   # Activer le binlog pour NDB
ndb_log_update_as_write=ON
ndb_log_updated_only=ON

[mysql_cluster]
ndb-connectstring=159.89.13.56:1186,159.89.13.57:1186
```

### 3.3 Demarrage du cluster (ordre)

```bash
# ================================================================
# PROCEDURE DE DEMARRAGE DU CLUSTER
# IMPORTANT : respecter l'ordre !
# ================================================================

# ── ETAPE 1 : Demarrer les Management Nodes ──

# Sur srv-mgmt-1 (159.89.13.56) :
sudo ndb_mgmd --initial \
  --config-file=/var/lib/mysql-cluster/config.ini \
  --configdir=/var/lib/mysql-cluster/mgmt

# Sur srv-mgmt-2 (159.89.13.57) :
sudo ndb_mgmd --initial \
  --config-file=/var/lib/mysql-cluster/config.ini \
  --configdir=/var/lib/mysql-cluster/mgmt

# Verifier :
ndb_mgm -e "SHOW"

# ── ETAPE 2 : Demarrer les Data Nodes ──

# Sur srv-data-1 (159.89.13.58) :
sudo ndbd --initial \
  --ndb-connectstring=159.89.13.56:1186,159.89.13.57:1186

# Sur srv-data-2 (159.89.13.59) :
sudo ndbd --initial \
  --ndb-connectstring=159.89.13.56:1186,159.89.13.57:1186

# Attendre que les 2 data nodes soient "started" :
ndb_mgm -e "ALL STATUS"
# Attendu : Node 3: started, Node 4: started

# ── ETAPE 3 : Demarrer les SQL Nodes ──

# Sur srv-sql-1 (159.89.13.54) :
sudo systemctl start mysql

# Sur srv-sql-2 (159.89.13.55) :
sudo systemctl start mysql

# ── ETAPE 4 : Verifier le cluster ──
ndb_mgm -e "SHOW"
# Attendu :
# [ndb_mgmd(MGM)] 2 node(s)
# id=1  @159.89.13.56  (mysql-8.0 ndb-8.0)
# id=2  @159.89.13.57  (mysql-8.0 ndb-8.0)
#
# [ndbd(NDB)]     2 node(s)
# id=3  @159.89.13.58  (mysql-8.0 ndb-8.0, Nodegroup: 0, *)
# id=4  @159.89.13.59  (mysql-8.0 ndb-8.0, Nodegroup: 0)
#
# [mysqld(API)]   2 node(s)
# id=5  @159.89.13.54  (mysql-8.0 ndb-8.0)
# id=6  @159.89.13.55  (mysql-8.0 ndb-8.0)
```

---

## 4. Schema de la base de donnees

### 4.1 Modele Entite-Relation (MER)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  MODELE ENTITE-RELATION (MER)                           │
│                  Base : ecolearnai_db                                   │
│                  Moteur : NDBCLUSTER                                    │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐       ┌──────────────────┐
  │ subscription_    │       │                  │
  │ plans            │       │     users        │
  │──────────────────│       │──────────────────│
  │ PK id            │       │ PK id            │
  │ UK code          │  ref  │ UK email         │
  │    name          │◄──────│    phone_number  │
  │    price         │       │    hashed_pass.  │
  │    currency      │       │    full_name     │
  │    duration_days │       │    gender        │
  │    is_active     │       │    role          │
  │    features      │       │    is_active     │
  │    sort_order    │       │    is_verified   │
  │    created_at    │       │    [champs RGPD] │
  │    updated_at    │       │    [gamification]│
  └──────────────────┘       │    created_at    │
                             │    updated_at    │
                             └──┬──┬──┬──┬──┬──┘
                                │  │  │  │  │
          ┌─────────────────────┘  │  │  │  └─────────────────────┐
          │                        │  │  │                        │
          ▼ 0..*                   │  │  │                    0..*▼
  ┌──────────────────┐             │  │  │          ┌──────────────────┐
  │  subscriptions   │             │  │  │          │user_achievements │
  │──────────────────│             │  │  │          │──────────────────│
  │ PK id            │             │  │  │          │ PK id            │
  │ FK user_id  ─────┤             │  │  │          │ FK user_id ──────┤
  │    plan          │             │  │  │          │ FK achievement_id│──┐
  │    price         │             │  │  │          │    unlocked_at   │  │
  │    currency      │             │  │  │          └──────────────────┘  │
  │    is_active     │             │  │  │                                │
  │    start_date    │             │  │  │          ┌──────────────────┐  │
  │    end_date      │             │  │  │          │   achievements   │  │
  │    auto_renew    │             │  │  │          │──────────────────│  │
  │    created_at    │             │  │  │          │ PK id            │◄─┘
  └──────┬───────────┘             │  │  │          │ UK code          │
         │                         │  │  │          │    name          │
     0..*│                         │  │  │          │    description   │
         ▼                         │  │  │          │    icon          │
  ┌──────────────────┐             │  │  │          │    category      │
  │    payments      │             │  │  │          │    xp_reward     │
  │──────────────────│             │  │  │          │    condition_type│
  │ PK id            │             │  │  │          │    condition_val │
  │ FK user_id  ─────┤             │  │  │          │    created_at    │
  │ FK subscription  │             │  │  │          └──────────────────┘
  │    _id           │             │  │  │
  │    amount        │             │  │  │
  │    currency      │             │  │  │
  │    payment_method│             │  │  │
  │    status        │             │  │  │
  │    transaction_  │             │  │  │
  │    ref           │             │  │  │
  │    invoice_number│             │  │  │
  │    invoice_det.  │             │  │  │
  │    paid_at       │             │  │  │
  │    moko_trans_   │             │  │  │
  │    uuid          │             │  │  │
  │    moko_pay_url  │             │  │  │
  │    created_at    │             │  │  │
  └──────────────────┘             │  │  │
                                   │  │  │
     ┌─────────────────────────────┘  │  └─────────────────────────────┐
     │                                │                                │
 0..*▼                            0..*▼                            0..*▼
  ┌──────────────────┐     ┌──────────────────┐         ┌──────────────────┐
  │  learning_paths  │     │ carbon_footprints│         │eco_compensations │
  │──────────────────│     │──────────────────│         │──────────────────│
  │ PK id            │     │ PK id            │         │ PK id            │
  │ FK user_id ──────┤     │ FK user_id ──────┤         │ FK user_id ──────┤
  │    title         │     │ FK session_id(UQ)│──┐      │    trees_planted │
  │    description   │     │    duration_min  │  │      │    co2_compens.  │
  │    subject       │     │    energy_kwh    │  │      │    partner_name  │
  │    difficulty    │     │    carbon_kg     │  │      │    partner_ref   │
  │    total_sessions│     │    server_region │  │      │    status        │
  │    completed_    │     │    carbon_factor │  │      │    notes         │
  │    sessions      │     │    created_at    │  │      │    triggered_at  │
  │    progress_%    │     └──────────────────┘  │      │    created_at    │
  │    status        │                           │      └──────────────────┘
  │    created_at    │                           │
  │    updated_at    │                           │
  └──────┬───────────┘                           │
         │                                       │
     0..*│                                       │
         ▼                                       │
  ┌──────────────────┐                           │
  │learning_sessions │                           │
  │──────────────────│                           │
  │ PK id            │◄──────────────────────────┘
  │ FK user_id ──────┤       (1..1 avec carbon_footprints)
  │ FK learning_path │
  │    _id           │
  │    title         │
  │    content       │
  │    ai_prompt_used│
  │    duration_min  │
  │    score         │
  │    session_number│
  │    status        │
  │    started_at    │
  │    completed_at  │
  │    created_at    │
  └──────────────────┘
```

### 4.2 Dictionnaire des tables

| # | Table | Lignes estimees | Taille estimee | Acces | Description |
|---|-------|----------------|----------------|-------|-------------|
| 1 | `users` | 10K-100K | 50-500 Mo | Tres frequent | Utilisateurs, RGPD chiffre |
| 2 | `subscriptions` | 10K-100K | 5-50 Mo | Frequent | Abonnements actifs/expires |
| 3 | `subscription_plans` | 5-20 | < 1 Mo | Cache (read) | Catalogue des plans |
| 4 | `payments` | 20K-200K | 20-200 Mo | Frequent | Historique paiements |
| 5 | `learning_paths` | 20K-200K | 10-100 Mo | Frequent | Parcours d'apprentissage |
| 6 | `learning_sessions` | 100K-1M | 100 Mo-1 Go | Tres frequent | Sessions + contenu IA |
| 7 | `carbon_footprints` | 100K-1M | 20-200 Mo | Modere | Empreintes carbone |
| 8 | `eco_compensations` | 1K-10K | < 5 Mo | Faible | Arbres plantes |
| 9 | `achievements` | 20-50 | < 1 Mo | Cache (read) | Catalogue badges |
| 10 | `user_achievements` | 50K-500K | 5-50 Mo | Modere | Badges debloques |
| 11 | `chat_messages` | 50K-500K | 20-200 Mo | Frequent | Messages chatbot IA |

---

## 5. Scripts SQL de creation

### 5.1 Creation de la base et de l'utilisateur

```sql
-- ================================================================
-- SCRIPT 1 : Initialisation de la base de donnees
-- Executer sur un SQL Node (srv-sql-1 ou srv-sql-2)
-- ================================================================

-- Creer la base de donnees
CREATE DATABASE IF NOT EXISTS ecolearnai_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Creer l'utilisateur applicatif
CREATE USER IF NOT EXISTS 'magma'@'%'
  IDENTIFIED BY 'YAN@mol1234';

-- Accorder les privileges
GRANT ALL PRIVILEGES ON ecolearnai_db.* TO 'magma'@'%';
FLUSH PRIVILEGES;

-- Creer un utilisateur lecture seule (pour le monitoring)
CREATE USER IF NOT EXISTS 'ecolearnai_readonly'@'%'
  IDENTIFIED BY 'ReadOnly@2026!';
GRANT SELECT ON ecolearnai_db.* TO 'ecolearnai_readonly'@'%';
FLUSH PRIVILEGES;

USE ecolearnai_db;
```

### 5.2 Creation des tables (moteur NDBCLUSTER)

```sql
-- ================================================================
-- SCRIPT 2 : Creation des tables (Engine = NDBCLUSTER)
-- IMPORTANT : NDB ne supporte pas les FK avec CASCADE
-- Les cascades sont gerees par l'application (SQLAlchemy)
-- ================================================================

USE ecolearnai_db;

-- ── Table : users ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              VARCHAR(36)   NOT NULL,
    email           VARCHAR(255)  NOT NULL,
    phone_number    VARCHAR(20)   DEFAULT NULL,
    hashed_password VARCHAR(255)  NOT NULL,

    -- Identite
    full_name       VARCHAR(255)  NOT NULL,
    gender          VARCHAR(20)   DEFAULT NULL,

    -- Donnees sensibles RGPD (chiffrees Fernet AES-128-CBC)
    encrypted_date_of_birth      TEXT DEFAULT NULL,
    encrypted_nationality        TEXT DEFAULT NULL,
    encrypted_national_id        TEXT DEFAULT NULL,
    national_id_type             VARCHAR(50) DEFAULT NULL,
    encrypted_address_line       TEXT DEFAULT NULL,
    encrypted_address_city       TEXT DEFAULT NULL,
    encrypted_address_postal_code TEXT DEFAULT NULL,
    encrypted_address_country    TEXT DEFAULT NULL,

    -- Verification SMS + Email
    verification_code            VARCHAR(10) DEFAULT NULL,
    verification_code_expires_at DATETIME DEFAULT NULL,
    is_email_verified            TINYINT(1) DEFAULT 0,

    -- Consentement RGPD
    gdpr_consent                 TINYINT(1) NOT NULL DEFAULT 0,
    gdpr_consent_at              DATETIME DEFAULT NULL,
    gdpr_marketing_consent       TINYINT(1) DEFAULT 0,
    gdpr_data_retention_consent  TINYINT(1) DEFAULT 0,

    -- Profil
    avatar_url      VARCHAR(500)  DEFAULT NULL,
    bio             TEXT          DEFAULT NULL,
    `language`      VARCHAR(10)   DEFAULT 'fr',
    timezone        VARCHAR(50)   DEFAULT 'Europe/Paris',

    -- Apprentissage
    `level`         VARCHAR(50)   DEFAULT 'debutant',
    objectives      TEXT          DEFAULT NULL,
    preferences     TEXT          DEFAULT NULL,

    -- Gamification
    total_xp              INT     DEFAULT 0,
    current_streak        INT     DEFAULT 0,
    longest_streak        INT     DEFAULT 0,
    last_activity_date    DATE    DEFAULT NULL,
    total_learning_minutes DOUBLE DEFAULT 0.0,

    -- Role & Statut
    `role`          VARCHAR(20)   DEFAULT 'user',
    is_active       TINYINT(1)    DEFAULT 1,
    is_verified     TINYINT(1)    DEFAULT 0,
    last_login_at   DATETIME      DEFAULT NULL,
    deactivated_at  DATETIME      DEFAULT NULL,

    -- Timestamps
    created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_users_email (email),
    KEY idx_users_phone (phone_number),
    KEY idx_users_role (role),
    KEY idx_users_active (is_active),
    KEY idx_users_verified (is_verified),
    KEY idx_users_created (created_at)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : subscription_plans ─────────────────────────
CREATE TABLE IF NOT EXISTS subscription_plans (
    id              VARCHAR(36)  NOT NULL,
    code            VARCHAR(50)  NOT NULL,
    name            VARCHAR(255) NOT NULL,
    description     TEXT         DEFAULT NULL,
    price           DOUBLE       NOT NULL,
    currency        VARCHAR(10)  DEFAULT 'USD',
    duration_days   INT          NOT NULL,
    is_active       TINYINT(1)   DEFAULT 1,
    features        TEXT         DEFAULT NULL,
    max_sessions_per_day INT     DEFAULT NULL,
    sort_order      INT          DEFAULT 0,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_plans_code (code),
    KEY idx_plans_active (is_active)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : subscriptions ──────────────────────────────
CREATE TABLE IF NOT EXISTS subscriptions (
    id              VARCHAR(36)  NOT NULL,
    user_id         VARCHAR(36)  NOT NULL,
    plan            VARCHAR(50)  NOT NULL,
    price           DOUBLE       NOT NULL,
    currency        VARCHAR(10)  DEFAULT 'EUR',
    is_active       TINYINT(1)   DEFAULT 1,
    start_date      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    end_date        DATETIME     NOT NULL,
    auto_renew      TINYINT(1)   DEFAULT 1,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_sub_user (user_id),
    KEY idx_sub_active (is_active),
    KEY idx_sub_plan (plan),
    KEY idx_sub_end (end_date)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : payments ───────────────────────────────────
CREATE TABLE IF NOT EXISTS payments (
    id                   VARCHAR(36)  NOT NULL,
    user_id              VARCHAR(36)  NOT NULL,
    subscription_id      VARCHAR(36)  NOT NULL,
    amount               DOUBLE       NOT NULL,
    currency             VARCHAR(10)  DEFAULT 'USD',
    payment_method       VARCHAR(50)  NOT NULL,
    status               VARCHAR(30)  DEFAULT 'pending',
    transaction_ref      VARCHAR(255) NOT NULL,
    invoice_number       VARCHAR(100) NOT NULL,
    invoice_details      TEXT         DEFAULT NULL,
    paid_at              DATETIME     DEFAULT NULL,
    created_at           DATETIME     DEFAULT CURRENT_TIMESTAMP,
    moko_transaction_uuid VARCHAR(255) DEFAULT NULL,
    moko_payment_url     TEXT         DEFAULT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uk_pay_txn_ref (transaction_ref),
    UNIQUE KEY uk_pay_invoice (invoice_number),
    KEY idx_pay_user (user_id),
    KEY idx_pay_sub (subscription_id),
    KEY idx_pay_status (status),
    KEY idx_pay_method (payment_method),
    KEY idx_pay_moko_uuid (moko_transaction_uuid),
    KEY idx_pay_paid_at (paid_at)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : learning_paths ─────────────────────────────
CREATE TABLE IF NOT EXISTS learning_paths (
    id                 VARCHAR(36)  NOT NULL,
    user_id            VARCHAR(36)  NOT NULL,
    title              VARCHAR(255) NOT NULL,
    description        TEXT         DEFAULT NULL,
    subject            VARCHAR(255) NOT NULL,
    difficulty         VARCHAR(50)  DEFAULT 'debutant',
    total_sessions     INT          DEFAULT 0,
    completed_sessions INT          DEFAULT 0,
    progress_percent   DOUBLE       DEFAULT 0.0,
    status             VARCHAR(30)  DEFAULT 'en_cours',
    created_at         DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_lp_user (user_id),
    KEY idx_lp_status (status),
    KEY idx_lp_subject (subject)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : learning_sessions ──────────────────────────
CREATE TABLE IF NOT EXISTS learning_sessions (
    id                VARCHAR(36)  NOT NULL,
    user_id           VARCHAR(36)  NOT NULL,
    learning_path_id  VARCHAR(36)  NOT NULL,
    title             VARCHAR(255) NOT NULL,
    content           TEXT         DEFAULT NULL,
    ai_prompt_used    TEXT         DEFAULT NULL,
    duration_minutes  DOUBLE       DEFAULT 0.0,
    score             DOUBLE       DEFAULT NULL,
    session_number    INT          NOT NULL,
    status            VARCHAR(30)  DEFAULT 'en_cours',
    started_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,
    completed_at      DATETIME     DEFAULT NULL,
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_ls_user (user_id),
    KEY idx_ls_path (learning_path_id),
    KEY idx_ls_status (status)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : carbon_footprints ──────────────────────────
CREATE TABLE IF NOT EXISTS carbon_footprints (
    id                VARCHAR(36)  NOT NULL,
    user_id           VARCHAR(36)  NOT NULL,
    session_id        VARCHAR(36)  NOT NULL,
    duration_minutes  DOUBLE       NOT NULL,
    energy_kwh        DOUBLE       NOT NULL,
    carbon_kg         DOUBLE       NOT NULL,
    server_region     VARCHAR(100) DEFAULT 'europe-west',
    carbon_factor     DOUBLE       NOT NULL,
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_cf_session (session_id),
    KEY idx_cf_user (user_id)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : eco_compensations ──────────────────────────
CREATE TABLE IF NOT EXISTS eco_compensations (
    id                  VARCHAR(36)  NOT NULL,
    user_id             VARCHAR(36)  NOT NULL,
    trees_planted       INT          NOT NULL,
    co2_compensated_kg  DOUBLE       NOT NULL,
    partner_name        VARCHAR(255) DEFAULT 'EcoTree Partner',
    partner_reference   VARCHAR(255) DEFAULT NULL,
    status              VARCHAR(30)  DEFAULT 'confirmed',
    notes               TEXT         DEFAULT NULL,
    triggered_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_ec_user (user_id),
    KEY idx_ec_status (status)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : achievements ───────────────────────────────
CREATE TABLE IF NOT EXISTS achievements (
    id               VARCHAR(36)  NOT NULL,
    code             VARCHAR(100) NOT NULL,
    name             VARCHAR(255) NOT NULL,
    description      TEXT         NOT NULL,
    icon             VARCHAR(50)  DEFAULT 'star',
    category         VARCHAR(50)  NOT NULL,
    xp_reward        INT          DEFAULT 0,
    condition_type   VARCHAR(100) NOT NULL,
    condition_value  INT          NOT NULL,
    created_at       DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_ach_code (code),
    KEY idx_ach_category (category)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : user_achievements ──────────────────────────
CREATE TABLE IF NOT EXISTS user_achievements (
    id              VARCHAR(36)  NOT NULL,
    user_id         VARCHAR(36)  NOT NULL,
    achievement_id  VARCHAR(36)  NOT NULL,
    unlocked_at     DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_ua_user (user_id),
    KEY idx_ua_achievement (achievement_id),
    UNIQUE KEY uk_ua_user_ach (user_id, achievement_id)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table : chat_messages ────────────────────────────
CREATE TABLE IF NOT EXISTS chat_messages (
    id                VARCHAR(36)  NOT NULL,
    user_id           VARCHAR(36)  NOT NULL,
    conversation_id   VARCHAR(36)  NOT NULL,
    role              VARCHAR(20)  NOT NULL,
    content           TEXT         NOT NULL,
    tokens_used       INT          DEFAULT 0,
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_cm_user (user_id),
    KEY idx_cm_conversation (conversation_id),
    KEY idx_cm_created (created_at)
) ENGINE=NDBCLUSTER DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.3 Insertion des plans par defaut

```sql
-- ================================================================
-- SCRIPT 3 : Donnees initiales
-- ================================================================

USE ecolearnai_db;

-- Plans d'abonnement
INSERT INTO subscription_plans (id, code, name, description, price, currency, duration_days, sort_order) VALUES
(UUID(), 'mensuel',     'Abonnement Mensuel',       'Acces complet pendant 30 jours',                    9.99,  'USD', 30,  1),
(UUID(), 'trimestriel', 'Abonnement Trimestriel',   'Acces complet pendant 3 mois - Economisez 15%',   24.99,  'USD', 90,  2),
(UUID(), 'annuel',      'Abonnement Annuel',         'Acces complet pendant 1 an - Economisez 30%',     89.99,  'USD', 365, 3);
```

---

## 6. Index et optimisation

### 6.1 Strategie d'indexation

```
┌──────────────────────────────────────────────────────────────────┐
│                     STRATEGIE D'INDEX                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Table          │ Index                  │ Type    │ Raison      │
│  ───────────────┼────────────────────────┼─────────┼──────────── │
│  users          │ PK(id)                 │ Hash    │ Lookup UUID │
│                 │ UK(email)              │ Hash    │ Login       │
│                 │ idx(phone_number)      │ Hash    │ Verif unique│
│                 │ idx(role)              │ Hash    │ Admin filter│
│                 │ idx(is_active)         │ Hash    │ Login check │
│                 │ idx(created_at)        │ Ordered │ Admin list  │
│  ───────────────┼────────────────────────┼─────────┼──────────── │
│  subscriptions  │ PK(id)                 │ Hash    │ Lookup      │
│                 │ idx(user_id)           │ Hash    │ Mes abonmts │
│                 │ idx(is_active)         │ Hash    │ Actifs      │
│                 │ idx(end_date)          │ Ordered │ Expiration  │
│  ───────────────┼────────────────────────┼─────────┼──────────── │
│  payments       │ PK(id)                 │ Hash    │ Lookup      │
│                 │ UK(transaction_ref)    │ Hash    │ Callback    │
│                 │ idx(user_id)           │ Hash    │ Mes paiem.  │
│                 │ idx(status)            │ Hash    │ Admin filter│
│                 │ idx(moko_trans_uuid)   │ Hash    │ Callback    │
│                 │ idx(paid_at)           │ Ordered │ Revenus     │
│  ───────────────┼────────────────────────┼─────────┼──────────── │
│  learning_sess. │ PK(id)                 │ Hash    │ Lookup      │
│                 │ idx(user_id)           │ Hash    │ Mes sessions│
│                 │ idx(learning_path_id)  │ Hash    │ Par parcours│
│                 │ idx(status)            │ Hash    │ Completes   │
│  ───────────────┼────────────────────────┼─────────┼──────────── │
│  carbon_footpr. │ UK(session_id)         │ Hash    │ 1:1 session │
│                 │ idx(user_id)           │ Hash    │ Mon carbone │
│                                                                  │
│  NOTE NDB :                                                      │
│  - NDB utilise des index Hash (par defaut) et Ordered (T-tree)  │
│  - Les index Hash sont optimaux pour les lookups par egalite    │
│  - Les index Ordered sont necessaires pour ORDER BY, BETWEEN    │
│  - Les colonnes TEXT/BLOB ne peuvent pas etre indexees en NDB   │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 Requetes critiques et leur optimisation

```sql
-- ── Requete 1 : Login (la plus frequente) ──
-- Index utilise : uk_users_email (Hash)
SELECT * FROM users WHERE email = 'jean@email.com';
-- Performance : O(1), < 1ms

-- ── Requete 2 : Dashboard admin (la plus lourde) ──
-- Utilise les index idx_pay_status, idx_pay_paid_at
SELECT COUNT(*), SUM(amount)
FROM payments
WHERE status = 'completed'
  AND paid_at >= '2026-02-01 00:00:00';
-- Optimisation : index composite (status, paid_at)

-- ── Requete 3 : Callback Moko (critique pour paiement) ──
-- Index utilise : idx_pay_moko_uuid (Hash)
SELECT * FROM payments WHERE moko_transaction_uuid = 'txn-uuid-...';
-- Performance : O(1), < 1ms

-- ── Requete 4 : Progression utilisateur ──
-- Index utilise : idx_ls_user + idx_ls_status
SELECT COUNT(*), AVG(score), SUM(duration_minutes)
FROM learning_sessions
WHERE user_id = 'uuid-...' AND status = 'terminee';
```

---

## 7. Replication et haute disponibilite

### 7.1 Comment NDB replique les donnees

```
┌──────────────────────────────────────────────────────────────────┐
│              REPLICATION SYNCHRONE NDB (NoOfReplicas=2)          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Quand le backend ecrit une donnee :                            │
│                                                                  │
│  Backend FastAPI                                                 │
│       │                                                          │
│       │ INSERT INTO users (...)                                  │
│       ▼                                                          │
│  SQL Node #1 (mysqld)                                            │
│       │                                                          │
│       │ Transaction NDB                                          │
│       ▼                                                          │
│  ┌─────────────┐    replication    ┌─────────────┐              │
│  │  DATA #1    │◄═══synchrone════►│  DATA #2    │              │
│  │  (ndbd)     │                  │  (ndbd)     │              │
│  │             │                  │             │              │
│  │  Partition  │                  │  Partition  │              │
│  │  primaire   │                  │  replica    │              │
│  │  (fragment) │                  │  (copie)    │              │
│  └─────────────┘                  └─────────────┘              │
│                                                                  │
│  Le COMMIT n'est retourne qu'apres ecriture sur LES DEUX noeuds│
│  => Aucune perte de donnees si un noeud tombe                   │
│                                                                  │
│  ──────────────────────────────────────────────────────────      │
│                                                                  │
│  SCENARIO DE PANNE :                                             │
│                                                                  │
│  Si DATA #1 tombe :                                              │
│  ┌─────────────┐                  ┌─────────────┐              │
│  │  DATA #1    │     X            │  DATA #2    │              │
│  │  (EN PANNE) │  deconnecte     │  (ACTIF)    │              │
│  │             │                  │             │              │
│  │             │                  │  Sert toutes│              │
│  │             │                  │  les donnees│              │
│  └─────────────┘                  └─────────────┘              │
│                                                                  │
│  - Les lectures/ecritures continuent via DATA #2                │
│  - Zero downtime, zero perte de donnees                         │
│  - Quand DATA #1 revient : resynchronisation automatique        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 7.2 Scenarios de panne et comportement

```
┌──────────────────────────────────────────────────────────────────┐
│             MATRICE DE TOLERANCE AUX PANNES                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Noeud en panne         │ Impact  │ Action automatique           │
│  ───────────────────────┼─────────┼──────────────────────────── │
│  1 Management Node      │ Aucun   │ L'autre mgmt prend le relai│
│  2 Management Nodes     │ CRITIQUE│ Cluster s'arrete            │
│  1 Data Node            │ Aucun   │ Replica sert les donnees   │
│  2 Data Nodes           │ CRITIQUE│ Cluster s'arrete            │
│  1 SQL Node             │ Faible  │ LB redirige vers l'autre   │
│  2 SQL Nodes            │ Eleve   │ Pas d'acces SQL (data OK)  │
│  1 Mgmt + 1 Data        │ Aucun   │ Chacun a son backup        │
│  1 Data + 1 SQL          │ Aucun   │ Les replicas servent       │
│                                                                  │
│  REGLE D'OR : Le cluster survit a la panne de N'IMPORTE QUEL   │
│  noeud unique. Seule la panne simultanée de 2 noeuds du meme   │
│  type est critique.                                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 8. Backup et restauration

### 8.1 Backup automatique (NDB natif)

```bash
# ================================================================
# BACKUP - Depuis le Management Node
# ================================================================

# Backup complet en ligne (sans arret du service)
ndb_mgm -e "START BACKUP"

# Backup avec compression
ndb_mgm -e "START BACKUP SNAPSHOTEND"

# Les fichiers sont sauves dans :
# /var/lib/mysql-cluster/data/BACKUP/BACKUP-<id>/
# Sur CHAQUE data node (redondant)

# ── Crontab pour backup quotidien ──
# Ajouter sur srv-mgmt-1 :
# 0 2 * * * ndb_mgm -e "START BACKUP" >> /var/log/ndb-backup.log 2>&1
```

### 8.2 Backup mysqldump (complementaire)

```bash
# ================================================================
# BACKUP SQL (depuis un SQL Node)
# Pour archivage long terme et migration
# ================================================================

# Backup complet de la base
mysqldump -u magma -p'YAN@mol1234' \
  --single-transaction \
  --routines \
  --triggers \
  ecolearnai_db > /backup/ecolearnai_$(date +%Y%m%d_%H%M%S).sql

# Backup compresse
mysqldump -u magma -p'YAN@mol1234' \
  ecolearnai_db | gzip > /backup/ecolearnai_$(date +%Y%m%d).sql.gz

# ── Crontab backup SQL quotidien ──
# 0 3 * * * mysqldump -u magma -p'YAN@mol1234' ecolearnai_db | gzip > /backup/ecolearnai_$(date +\%Y\%m\%d).sql.gz
```

### 8.3 Restauration

```bash
# ── Restauration NDB (depuis le management node) ──
ndb_mgm -e "ALL STOP"
# Puis redemarrer avec --initial et restaurer :
ndb_restore --ndb-connectstring=159.89.13.56:1186 \
  --backupid=<BACKUP_ID> \
  --nodeid=3 \
  --restore-data \
  --backup-path=/var/lib/mysql-cluster/data/BACKUP/BACKUP-<id>

# ── Restauration SQL (depuis un dump) ──
mysql -u magma -p'YAN@mol1234' ecolearnai_db < /backup/ecolearnai_20260209.sql
```

---

## 9. Monitoring et maintenance

### 9.1 Commandes de monitoring NDB

```bash
# ── Etat du cluster ──
ndb_mgm -e "SHOW"
ndb_mgm -e "ALL STATUS"

# ── Memoire des data nodes ──
ndb_mgm -e "ALL REPORT MEMORYUSAGE"
# Exemple sortie :
# Node 3: Data usage is 45%(2304M of 4096M)
# Node 3: Index usage is 30%(153M of 512M)
# Node 4: Data usage is 45%(2304M of 4096M)
# Node 4: Index usage is 30%(153M of 512M)

# ── Etat des backups ──
ndb_mgm -e "ALL REPORT BACKUPSTATUS"

# ── Statistiques des transactions ──
ndb_mgm -e "ALL REPORT EventSubscription"

# ── Verifier les erreurs ──
ndb_mgm -e "ALL ERROR"

# ── Logs du cluster ──
tail -f /var/lib/mysql-cluster/mgmt/ndb_1_cluster.log
```

### 9.2 Requetes de monitoring SQL

```sql
-- ── Etat du cluster depuis MySQL ──
SHOW ENGINE NDBCLUSTER STATUS\G

-- ── Tables NDB et leur taille ──
SELECT
  TABLE_NAME,
  TABLE_ROWS,
  ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
  ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
  ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'ecolearnai_db'
ORDER BY DATA_LENGTH DESC;

-- ── Connexions actives ──
SHOW PROCESSLIST;

-- ── Variables NDB ──
SHOW VARIABLES LIKE 'ndb%';

-- ── Statistiques NDB ──
SELECT * FROM ndbinfo.memoryusage;
SELECT * FROM ndbinfo.nodes;
SELECT * FROM ndbinfo.transporters;

-- ── Requetes lentes ──
SELECT * FROM mysql.slow_log
ORDER BY start_time DESC LIMIT 20;
```

### 9.3 Script de healthcheck

```bash
#!/bin/bash
# ================================================================
# healthcheck_cluster.sh - Verification sante du cluster NDB
# Placer sur srv-mgmt-1, executer via cron toutes les 5 minutes
# ================================================================

LOG="/var/log/ndb-healthcheck.log"
ALERT_EMAIL="admin@ecolearnai.com"

echo "$(date) - Debut healthcheck" >> $LOG

# Verifier que tous les noeuds sont connectes
STATUS=$(ndb_mgm -e "ALL STATUS" 2>/dev/null)

# Compter les noeuds "started"
STARTED=$(echo "$STATUS" | grep -c "started")

if [ "$STARTED" -lt 4 ]; then
    echo "$(date) - ALERTE : Seulement $STARTED/4 noeuds started !" >> $LOG
    echo "$STATUS" >> $LOG

    # Envoyer alerte
    echo "NDB Cluster EcoLearnAI : $STARTED/4 noeuds actifs. Verifiez immediatement." \
      | mail -s "ALERTE NDB Cluster" $ALERT_EMAIL
else
    echo "$(date) - OK : $STARTED/4 noeuds started" >> $LOG
fi

# Verifier la memoire
MEMUSE=$(ndb_mgm -e "ALL REPORT MEMORYUSAGE" 2>/dev/null)
echo "$MEMUSE" >> $LOG

# Alerter si memoire > 80%
HIGH_MEM=$(echo "$MEMUSE" | grep -oP '\d+(?=%)' | awk '$1 > 80')
if [ ! -z "$HIGH_MEM" ]; then
    echo "$(date) - ALERTE : Memoire NDB > 80% !" >> $LOG
    echo "Memoire NDB critique. Details: $MEMUSE" \
      | mail -s "ALERTE NDB Memoire" $ALERT_EMAIL
fi

echo "$(date) - Fin healthcheck" >> $LOG
```

---

## 10. Connexion depuis le backend FastAPI

### 10.1 Configuration avec ProxySQL (recommande)

```
┌────────────────────────────────────────────────────────────────┐
│         CONNEXION BACKEND -> PROXYSQL -> SQL NODES             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Backend FastAPI                                               │
│  DATABASE_URL = mysql+pymysql://magma:YAN%40mol1234            │
│                 @159.89.13.54:6033/ecolearnai_db               │
│       │                    ▲                                   │
│       │                    │ Port 6033                         │
│       ▼                    │                                   │
│  ProxySQL (sur srv-sql-1)  │                                   │
│  ┌─────────────────────────┴──────┐                           │
│  │ Hostgroup 0 (Read/Write)      │                            │
│  │   → srv-sql-1:3306 (poids 100)│                            │
│  │   → srv-sql-2:3306 (poids 100)│                            │
│  │                                │                            │
│  │ Health check : SELECT 1       │                            │
│  │ Interval : 2000ms              │                            │
│  │ Max connections : 500          │                            │
│  └────────────────────────────────┘                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 10.2 Configuration directe (actuelle)

```python
# backend/app/config.py (configuration actuelle)
DATABASE_URL = "mysql+pymysql://magma:YAN%40mol1234@159.89.13.54:3306/ecolearnai_db?charset=utf8mb4"

# Configuration cluster avec failover automatique :
# Utiliser les 2 SQL nodes dans l'URL (PyMySQL supporte le failover)
DATABASE_URL = "mysql+pymysql://magma:YAN%40mol1234@159.89.13.54:3306/ecolearnai_db?charset=utf8mb4"
DATABASE_URL_FAILOVER = "mysql+pymysql://magma:YAN%40mol1234@159.89.13.55:3306/ecolearnai_db?charset=utf8mb4"
```

### 10.3 Configuration SQLAlchemy optimisee pour NDB

```python
# backend/app/database.py (optimise pour NDB Cluster)
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Verifier la connexion avant utilisation
    pool_recycle=3600,           # Recycler les connexions toutes les heures
    pool_size=20,                # 20 connexions permanentes dans le pool
    max_overflow=30,             # 30 connexions supplementaires en cas de charge
    pool_timeout=30,             # Timeout si pas de connexion disponible
    echo=False,                  # Pas de log SQL en production
    connect_args={
        "connect_timeout": 10,   # Timeout connexion MySQL
        "read_timeout": 30,      # Timeout lecture
        "write_timeout": 30,     # Timeout ecriture
        "charset": "utf8mb4",
    },
)

# Event : forcer le moteur NDBCLUSTER pour les CREATE TABLE
@event.listens_for(engine, "connect")
def set_ndb_engine(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET ndb_table_no_logging=0")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 11. Resume de l'architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     RESUME ARCHITECTURE NDB CLUSTER                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Composant              │ Nombre │ Specs              │ Role         │
│  ───────────────────────┼────────┼────────────────────┼──────────── │
│  Management Nodes       │   2    │ 2Go RAM, 2 vCPU    │ Config &    │
│  (ndb_mgmd)             │        │ 20Go SSD           │ supervision │
│  ───────────────────────┼────────┼────────────────────┼──────────── │
│  Data Nodes             │   2    │ 8Go RAM, 4 vCPU    │ Stockage &  │
│  (ndbd)                 │        │ 100Go SSD          │ replication │
│  ───────────────────────┼────────┼────────────────────┼──────────── │
│  SQL Nodes              │   2    │ 4Go RAM, 2 vCPU    │ Acces SQL   │
│  (mysqld)               │        │ 50Go SSD           │ (Active/Act)│
│  ───────────────────────┼────────┼────────────────────┼──────────── │
│  Total serveurs         │  4-6   │ 28Go RAM total     │             │
│  Total stockage         │        │ 340Go SSD total    │             │
│                                                                      │
│  Base de donnees        : ecolearnai_db                              │
│  Nombre de tables       : 11                                         │
│  Moteur de stockage     : NDBCLUSTER                                │
│  Replication            : Synchrone (NoOfReplicas=2)                │
│  Partitionnement        : Automatique (hash sur PK)                 │
│  Tolerance aux pannes   : 1 noeud de chaque type                    │
│  Backup                 : NDB natif (quotidien) + mysqldump         │
│  Chiffrement applicatif : Fernet AES-128-CBC (7 champs RGPD)       │
│  Connexion backend      : PyMySQL + SQLAlchemy (pool=20, overflow=30)│
│                                                                      │
│  Cout estime            :                                            │
│  - DigitalOcean: ~$100-150/mois (4 droplets + stockage)             │
│  - AWS RDS: Non applicable (NDB = auto-gere)                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 11. Redis - Cache et Rate Limiting

### 11.1 Architecture Redis

```
┌──────────────────────────────────────────────────────────────────┐
│                    REDIS - COUCHE CACHE                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐                                         │
│  │  Backend FastAPI    │                                         │
│  │                    │                                         │
│  │  cache_service.py  │──── SET/GET ────►┌──────────────────┐  │
│  │  (redis-py 5.0)    │                  │  Redis 7.2       │  │
│  │                    │◄── JSON data ────│  (Alpine)        │  │
│  └────────────────────┘                  │                  │  │
│                                          │  256 Mo RAM      │  │
│  Flux d'une requete :                    │  LRU eviction    │  │
│                                          │  AOF persistence │  │
│  1. Requete HTTP                         │  Port: 6379      │  │
│  2. Verifier Redis (cache_get)           │                  │  │
│     → HIT  : retourner directement       │  Donnees :       │  │
│     → MISS : interroger MySQL            │  - Plans (10min) │  │
│  3. Stocker en cache (cache_set + TTL)   │  - Dashboard 2m  │  │
│  4. Retourner la reponse                 │  - User dash 3m  │  │
│                                          │  - OTP attempts  │  │
│                                          │  - Rate limits   │  │
│                                          └──────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 11.2 Configuration Redis (docker-compose)

```yaml
redis:
  image: redis:7.2-alpine
  container_name: ecolearnai-redis
  restart: always
  command: >
    redis-server
    --requirepass EcoLearn@Redis2026
    --maxmemory 256mb                  # Limite memoire
    --maxmemory-policy allkeys-lru     # Eviction LRU quand plein
    --appendonly yes                    # Persistence AOF
    --appendfsync everysec             # Sync disque chaque seconde
    --save 900 1                       # Snapshot si 1 modif en 15min
    --save 300 10                      # Snapshot si 10 modifs en 5min
    --save 60 10000                    # Snapshot si 10000 modifs en 1min
    --tcp-keepalive 60                 # Keepalive 60s
    --timeout 300                      # Deconnexion apres 5min inactif
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data                 # Persistence sur disque
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "EcoLearn@Redis2026", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### 11.3 Cles de cache et TTL

```
┌──────────────────────────────────────────────────────────────────┐
│                    STRATEGIE DE CACHE                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Prefixe global : ecolearnai:                                   │
│                                                                  │
│  Cle                           │ TTL    │ Usage                  │
│  ──────────────────────────────┼────────┼─────────────────────── │
│  ecolearnai:plans:active       │ 10 min │ Plans d'abonnement    │
│  ecolearnai:admin:dashboard    │  2 min │ Dashboard admin       │
│  ecolearnai:dashboard:user:{id}│  3 min │ Dashboard utilisateur │
│  ecolearnai:otp_attempts:{id}  │ 15 min │ Anti brute-force OTP  │
│  ecolearnai:ratelimit:{ip}     │  1 min │ Rate limiting API     │
│                                                                  │
│  Invalidation :                                                  │
│  - Modification plan  → invalidate plans:*                      │
│  - Modification user  → invalidate dashboard:user:{id}          │
│  - Modification admin → invalidate admin:dashboard              │
│  - Admin flush cache  → POST /api/monitoring/cache/flush        │
│                                                                  │
│  Politique d'eviction : allkeys-lru                             │
│  (Supprime les cles les moins recemment utilisees quand         │
│   la memoire est pleine)                                        │
│                                                                  │
│  Mode degradé :                                                 │
│  Si Redis est indisponible, l'application continue sans cache.  │
│  Toutes les operations cache retournent None/False.             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 11.4 Utilisation dans le code

```python
# backend/app/services/cache_service.py

# ── Operations de base ──
from app.services.cache_service import cache_get, cache_set, cache_delete

# Lire du cache
data = cache_get("plans:active")          # → dict/list ou None

# Ecrire dans le cache
cache_set("plans:active", plans_list, ttl=600)  # 10 minutes

# Supprimer une cle
cache_delete("plans:active")

# Supprimer par pattern
cache_delete_pattern("dashboard:user:*")  # Tous les dashboards user

# ── Cache specialise ──
from app.services.cache_service import (
    cache_get_plans, cache_set_plans, cache_invalidate_plans,
    cache_get_admin_dashboard, cache_set_admin_dashboard,
    cache_get_user_dashboard, cache_set_user_dashboard,
    cache_otp_attempt, cache_otp_is_blocked,
    cache_rate_limit,
)

# Anti brute-force OTP
attempts = cache_otp_attempt(user_id)     # Incremente + retourne le compteur
if cache_otp_is_blocked(user_id):         # True si >= 5 tentatives en 15min
    raise HTTPException(429, "Trop de tentatives")

# Rate limiting
if not cache_rate_limit(client_ip, window_seconds=60, max_requests=60):
    raise HTTPException(429, "Trop de requetes")
```

---

## 12. Stack de Monitoring (Prometheus + Grafana)

### 12.1 Architecture de monitoring

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    STACK DE MONITORING                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                          ┌───────────────────┐                          │
│                          │    GRAFANA         │                          │
│                          │    :3000           │                          │
│                          │                    │                          │
│                          │  Dashboards :      │                          │
│                          │  - Vue d'ensemble  │                          │
│                          │  - Backend FastAPI │                          │
│                          │  - Redis           │                          │
│                          │  - MySQL           │                          │
│                          │  - Systeme (OS)    │                          │
│                          └────────┬───────────┘                          │
│                                   │ PromQL queries                       │
│                          ┌────────▼───────────┐                          │
│                          │    PROMETHEUS       │                          │
│                          │    :9090            │                          │
│                          │                    │                          │
│                          │  Retention: 30j    │                          │
│                          │  Scrape: 15s       │                          │
│                          │  Alertes           │                          │
│                          └──┬──┬──┬──┬───────┘                          │
│                             │  │  │  │                                   │
│          ┌──────────────────┘  │  │  └──────────────────┐               │
│          │                     │  │                     │               │
│    ┌─────▼──────┐  ┌──────────▼──▼─────┐   ┌──────────▼──────┐        │
│    │ Backend    │  │  Redis Exporter   │   │ Node Exporter   │        │
│    │ FastAPI    │  │  :9121            │   │ :9100           │        │
│    │ /metrics   │  │                   │   │                 │        │
│    │ :8000      │  │  Metriques Redis  │   │ CPU, RAM, Disk  │        │
│    │            │  │  memoire, cles,   │   │ Reseau, I/O     │        │
│    │ HTTP stats │  │  hits/misses,     │   │                 │        │
│    │ Latence    │  │  connexions       │   │                 │        │
│    │ Erreurs    │  │                   │   │                 │        │
│    └────────────┘  └───────────────────┘   └─────────────────┘        │
│                                                                          │
│    ┌────────────┐                                                        │
│    │ MySQL      │                                                        │
│    │ Exporter   │                                                        │
│    │ :9104      │                                                        │
│    │            │                                                        │
│    │ Connexions │                                                        │
│    │ QPS, Slow  │                                                        │
│    │ Queries    │                                                        │
│    └────────────┘                                                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 12.2 Services Docker de monitoring

| Service | Image | Port | Role |
|---------|-------|------|------|
| `prometheus` | prom/prometheus:v2.51.0 | 9090 | Collecte et stockage des metriques |
| `grafana` | grafana/grafana:10.4.1 | 3000 | Dashboards visuels et alertes |
| `node-exporter` | prom/node-exporter:v1.7.0 | 9100 | Metriques OS (CPU, RAM, Disque) |
| `redis-exporter` | oliver006/redis_exporter:v1.58.0 | 9121 | Metriques Redis |
| `mysql-exporter` | prom/mysqld-exporter:v0.15.1 | 9104 | Metriques MySQL |

### 12.3 Acces Grafana

```
URL      : http://votre-serveur:3000
Login    : admin
Password : EcoLearn@Grafana2026

Dashboard pre-configure : "EcoLearn AI - Vue d'ensemble"
  - Requetes/seconde du backend
  - Latence P50/P95
  - Memoire Redis + Hit/Miss ratio
  - Connexions MySQL + QPS
  - CPU, RAM, Disque du serveur
  - Trafic reseau
```

### 12.4 Regles d'alerte Prometheus

```
┌──────────────────────────────────────────────────────────────────┐
│                    REGLES D'ALERTE                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Alerte                  │ Seuil        │ Severite  │ Delai     │
│  ────────────────────────┼──────────────┼───────────┼────────── │
│  BackendDown             │ up == 0      │ CRITICAL  │ 1 min     │
│  HighErrorRate           │ 5xx > 5%     │ WARNING   │ 5 min     │
│  HighLatency             │ P95 > 2s     │ WARNING   │ 5 min     │
│  RedisDown               │ up == 0      │ CRITICAL  │ 1 min     │
│  RedisHighMemory         │ > 85%        │ WARNING   │ 5 min     │
│  RedisTooManyConnections │ > 100        │ WARNING   │ 5 min     │
│  RedisHighEviction       │ > 10 cles/s  │ WARNING   │ 5 min     │
│  MySQLDown               │ up == 0      │ CRITICAL  │ 1 min     │
│  MySQLHighConnections    │ > 80%        │ WARNING   │ 5 min     │
│  MySQLSlowQueries        │ > 0.5/s      │ WARNING   │ 10 min    │
│  HighCPUUsage            │ > 85%        │ WARNING   │ 10 min    │
│  HighMemoryUsage         │ > 90%        │ CRITICAL  │ 5 min     │
│  DiskSpaceLow            │ > 85%        │ WARNING   │ 10 min    │
│  DiskSpaceCritical       │ > 95%        │ CRITICAL  │ 5 min     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 13. Cron Backup - Replication automatique

### 13.1 Architecture de backup

```
┌──────────────────────────────────────────────────────────────────────────┐
│             REPLICATION CRON - CHAQUE JOUR A 1H DU MATIN                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐                                                 │
│  │  Backend FastAPI    │                                                 │
│  │                    │                                                 │
│  │  APScheduler       │  Cron: chaque jour a 01:00 UTC                  │
│  │  (BackgroundSched.)│                                                 │
│  │                    │                                                 │
│  │  backup_service.py │                                                 │
│  └──────┬─────────────┘                                                 │
│         │                                                                │
│         │  Pour chaque table (11 tables) :                              │
│         │  1. SELECT * FROM table (source)                              │
│         │  2. DELETE FROM table (backup)                                │
│         │  3. INSERT par lots de 500 lignes (backup)                    │
│         │                                                                │
│         ▼                                     ▼                         │
│  ┌──────────────────┐              ┌──────────────────┐                 │
│  │  BASE SOURCE     │              │  BASE BACKUP     │                 │
│  │  (Principale)    │   ────►      │  (Dupliquee)     │                 │
│  │                  │  Replication  │                  │                 │
│  │  159.89.13.54    │  complete    │  159.89.13.55    │                 │
│  │  :3306           │  (truncate   │  :3306           │                 │
│  │                  │  + insert)   │                  │                 │
│  │  ecolearnai_db   │              │  ecolearnai_db   │                 │
│  │                  │              │  _backup         │                 │
│  └──────────────────┘              └──────────────────┘                 │
│                                                                          │
│  En cas d'echec :                                                        │
│  - Log d'erreur detaille                                                │
│  - Email d'alerte envoye a l'administrateur                             │
│  - Historique des 30 derniers backups conserve en memoire               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 13.2 Configuration

```python
# Variables d'environnement (docker-compose.yml)
BACKUP_DATABASE_URL=mysql+pymysql://magma:YAN%40mol1234@159.89.13.55:3306/ecolearnai_db_backup?charset=utf8mb4
BACKUP_CRON_HOUR=1           # 1h du matin
BACKUP_CRON_MINUTE=0         # minute 0
BACKUP_ENABLED=true          # Activer/desactiver
```

### 13.3 Preparation de la base de backup

```sql
-- ================================================================
-- A executer sur le serveur de backup (159.89.13.55)
-- ================================================================

-- Creer la base de backup
CREATE DATABASE IF NOT EXISTS ecolearnai_db_backup
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Accorder les privileges a l'utilisateur magma
GRANT ALL PRIVILEGES ON ecolearnai_db_backup.* TO 'magma'@'%';
FLUSH PRIVILEGES;

-- Les tables sont creees automatiquement par le service de backup
-- (synchronisation du schema depuis la base source)
```

### 13.4 Processus de backup detaille

```
┌──────────────────────────────────────────────────────────────────┐
│                    PROCESSUS DE BACKUP                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  01:00:00 UTC  │ APScheduler declenche run_backup()             │
│  01:00:01      │ Connexion a la base source (159.89.13.54)      │
│  01:00:02      │ Connexion a la base backup (159.89.13.55)      │
│  01:00:03      │ Synchronisation du schema (CREATE TABLE IF NOT)│
│                │                                                 │
│  01:00:04      │ Table 1/11 : subscription_plans                │
│                │   SELECT * → 3 lignes                          │
│                │   DELETE + INSERT → 3 lignes copiees (0.1s)    │
│  01:00:05      │ Table 2/11 : achievements                      │
│                │   SELECT * → 25 lignes                         │
│                │   DELETE + INSERT → 25 lignes copiees (0.2s)   │
│  01:00:06      │ Table 3/11 : users                             │
│                │   SELECT * → 5,000 lignes                      │
│                │   DELETE + INSERT (10 lots de 500) → (2.5s)    │
│  ...           │ ...                                            │
│  01:00:15      │ Table 10/11 : user_achievements                │
│                │   SELECT * → 12,000 lignes                     │
│                │   DELETE + INSERT (24 lots de 500) → (4.2s)    │
│  01:00:16      │ Table 11/11 : chat_messages                    │
│                │   SELECT * → ... lignes                        │
│                │   DELETE + INSERT (lots de 500) → (...)        │
│                │                                                 │
│  01:00:20      │ RESULTAT :                                     │
│                │   Status : SUCCESS                              │
│                │   Tables : 11/11                                │
│                │   Lignes : 45,328                               │
│                │   Duree  : 20 secondes                         │
│                │                                                 │
│  01:00:21      │ Historique mis a jour                           │
│                │ next_run = demain 01:00:00 UTC                  │
│                                                                  │
│  ORDRE DES TABLES (respecte les FK logiques) :                  │
│  1. subscription_plans  (reference par subscriptions)           │
│  2. achievements        (reference par user_achievements)       │
│  3. users               (reference par toutes les autres)       │
│  4. subscriptions       (FK → users)                            │
│  5. payments            (FK → users, subscriptions)             │
│  6. learning_paths      (FK → users)                            │
│  7. learning_sessions   (FK → users, learning_paths)            │
│  8. carbon_footprints   (FK → users, learning_sessions)         │
│  9. eco_compensations   (FK → users)                            │
│ 10. user_achievements   (FK → users, achievements)              │
│ 11. chat_messages      (FK → users)                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 13.5 En cas de perte de la base principale

```bash
# ================================================================
# PROCEDURE DE RESTAURATION DEPUIS LA BASE DE BACKUP
# A executer en urgence si la base principale est perdue
# ================================================================

# 1. Exporter la base de backup
mysqldump -h 159.89.13.55 -u magma -p'YAN@mol1234' \
  ecolearnai_db_backup > /tmp/ecolearnai_restore.sql

# 2. Recreer la base principale (si le serveur est de retour)
mysql -h 159.89.13.54 -u magma -p'YAN@mol1234' \
  -e "CREATE DATABASE IF NOT EXISTS ecolearnai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. Restaurer les donnees
mysql -h 159.89.13.54 -u magma -p'YAN@mol1234' \
  ecolearnai_db < /tmp/ecolearnai_restore.sql

# 4. OU pointer le backend vers la base de backup temporairement
# Modifier dans docker-compose.yml :
#   DATABASE_URL=mysql+pymysql://magma:YAN%40mol1234@159.89.13.55:3306/ecolearnai_db_backup?charset=utf8mb4
# Puis :
docker compose up -d --build backend
```

---

## 14. Endpoints API de monitoring

### 14.1 Liste des endpoints

```
┌──────────────────────────────────────────────────────────────────┐
│                    ENDPOINTS DE MONITORING                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Endpoint                       │ Auth  │ Description            │
│  ──────────────────────────────┼───────┼─────────────────────── │
│  GET  /health                  │ Non   │ Health check simple    │
│  GET  /metrics                 │ Non   │ Metriques Prometheus   │
│  GET  /api/monitoring/health   │ Non   │ Health check detaille  │
│  GET  /api/monitoring/system   │ Admin │ CPU, RAM, Disque, Net  │
│  GET  /api/monitoring/redis    │ Admin │ Stats Redis detaillees │
│  GET  /api/monitoring/database │ Admin │ Stats MySQL detaillees │
│  GET  /api/monitoring/backup   │ Admin │ Statut cron backup     │
│  POST /api/monitoring/cache/flush│Admin│ Vider le cache Redis   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 14.2 Exemples curl

```bash
# ── Health check detaille (public) ──
curl http://localhost:8000/api/monitoring/health

# Reponse :
# {
#   "status": "healthy",
#   "timestamp": "2026-02-09T12:00:00",
#   "checks": {
#     "backend":    { "status": "up", "uptime": "2j 5h 30m" },
#     "database":   { "status": "up", "version": "8.0.35-ndb-8.0" },
#     "redis":      { "status": "up", "keys": 142, "memory": "15.2M" },
#     "ai_service": { "status": "up" },
#     "backup":     { "last_status": "success", "last_run": "01:00:20" }
#   }
# }

# ── Metriques systeme (admin) ──
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/system

# ── Stats Redis (admin) ──
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/redis

# ── Stats MySQL (admin) ──
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/database

# ── Statut backup (admin) ──
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/backup

# ── Vider le cache (admin) ──
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/cache/flush
```

---

## 15. Resume de l'architecture complete

```
┌──────────────────────────────────────────────────────────────────────────┐
│                 ARCHITECTURE COMPLETE ECOLEARNAI                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    SERVICES APPLICATIFS                          │    │
│  │                                                                  │    │
│  │  Backend FastAPI (:8000)      AI Service Flask (:5000)          │    │
│  │  ├── SQLAlchemy (MySQL)       ├── OpenAI GPT                    │    │
│  │  ├── Redis (cache)            └── Generation contenu IA         │    │
│  │  ├── APScheduler (cron)                                         │    │
│  │  ├── Prometheus metrics                                         │    │
│  │  └── Monitoring endpoints                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    COUCHE DONNEES                                │    │
│  │                                                                  │    │
│  │  Redis 7.2 (:6379)           MySQL NDB Cluster (:3306)          │    │
│  │  ├── Cache 256 Mo            ├── 2 Management Nodes             │    │
│  │  ├── LRU eviction            ├── 2 Data Nodes (8 Go RAM)        │    │
│  │  ├── AOF persistence         ├── 2 SQL Nodes                    │    │
│  │  ├── Rate limiting           ├── Replication synchrone          │    │
│  │  └── Anti brute-force        └── 11 tables NDBCLUSTER           │    │
│  │                                                                  │    │
│  │  MySQL Backup (:3306)                                           │    │
│  │  ├── 159.89.13.55                                               │    │
│  │  ├── ecolearnai_db_backup                                       │    │
│  │  └── Replication cron 01:00 UTC                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    MONITORING                                    │    │
│  │                                                                  │    │
│  │  Prometheus (:9090)           Grafana (:3000)                   │    │
│  │  ├── Scrape 15s              ├── Dashboard auto-provisionne     │    │
│  │  ├── Retention 30j           ├── Login admin/EcoLearn@Grafana   │    │
│  │  ├── 14 regles d'alerte      └── 10 panneaux temps reel        │    │
│  │  └── 5 exporters                                                │    │
│  │                                                                  │    │
│  │  Node Exporter (:9100)        Redis Exporter (:9121)            │    │
│  │  MySQL Exporter (:9104)                                         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ══════════════════════════════════════════════════════════════════      │
│  TOTAL SERVICES DOCKER : 8                                               │
│  ──────────────────────────────────────────────────────────────────      │
│  1. backend           (FastAPI + cron backup + cache client)            │
│  2. ai-service        (Flask + OpenAI)                                  │
│  3. redis             (Cache + Rate Limiting)                           │
│  4. prometheus         (Collecte metriques)                             │
│  5. grafana           (Dashboards visuels)                              │
│  6. node-exporter     (Metriques OS)                                    │
│  7. redis-exporter    (Metriques Redis)                                 │
│  8. mysql-exporter    (Metriques MySQL)                                 │
│  ══════════════════════════════════════════════════════════════════      │
│                                                                          │
│  PORTS EXPOSES :                                                         │
│  8000  - Backend API                                                     │
│  5000  - AI Service                                                      │
│  6379  - Redis                                                           │
│  3306  - MySQL (distant)                                                 │
│  9090  - Prometheus                                                      │
│  3000  - Grafana                                                         │
│  9100  - Node Exporter                                                   │
│  9121  - Redis Exporter                                                  │
│  9104  - MySQL Exporter                                                  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Demarrage complet

```bash
# Demarrer tous les services
docker compose up -d

# Verifier l'etat
docker compose ps

# Verifier le health check
curl http://localhost:8000/api/monitoring/health

# Acceder a Grafana
# → http://localhost:3000 (admin / EcoLearn@Grafana2026)

# Acceder a Prometheus
# → http://localhost:9090

# Verifier les metriques FastAPI
curl http://localhost:8000/metrics
```

---

*Document genere le 11/02/2026 - EcoLearn AI v1.4.0*
