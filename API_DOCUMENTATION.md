# EcoLearn AI - Documentation API Complete

**Version** : 1.4.0
**Base URL** : `http://localhost:8000`
**Documentation interactive** : `http://localhost:8000/docs` (Swagger UI) | `http://localhost:8000/redoc` (ReDoc)

---

## Table des matieres

1. [Deploiement](#1-deploiement)
2. [Architecture & Technologies](#2-architecture--technologies)
3. [Authentification (JWT)](#3-authentification-jwt)
4. [Flux d'inscription complet](#4-flux-dinscription-complet)
5. [Endpoints API](#5-endpoints-api)
   - [Root & Health](#51-root--health)
   - [Authentification](#52-authentification)
   - [Utilisateurs & Profil](#53-utilisateurs--profil)
   - [RGPD / GDPR](#54-rgpd--gdpr)
   - [Abonnements](#55-abonnements)
   - [Paiements & Factures](#56-paiements--factures)
   - [Apprentissage](#57-apprentissage)
   - [Empreinte Carbone](#58-empreinte-carbone)
   - [Tableau de Bord](#59-tableau-de-bord)
   - [Administration](#510-administration)
   - [Monitoring](#511-monitoring)
   - [Chatbot IA](#512-chatbot-ia)
6. [Modeles de donnees (Schemas)](#6-modeles-de-donnees-schemas)
7. [Codes d'erreur](#7-codes-derreur)
8. [Securite & RGPD](#8-securite--rgpd)
9. [Exemples d'integration Frontend](#9-exemples-dintegration-frontend)

---

## 1. Deploiement

### Pre-requis

- **Docker** >= 24.x
- **Docker Compose** >= 2.x
- Une cle API OpenAI (pour le service IA)
- Une cle API Moko Checkout / FreshPay (pour les paiements carte)
- Une cle API MGT-SMS (pour l'envoi de SMS)
- Un compte Gmail avec mot de passe d'application (pour l'envoi d'emails)

### Etape 1 : Cloner et configurer

```bash
# Cloner le projet
git clone <url-du-repo>
cd ProEcoIt

# Copier le fichier d'environnement
cp .env.example .env
```

### Etape 2 : Configurer le fichier `.env`

Editer le fichier `.env` et renseigner les valeurs reelles :

```env
# ===== OBLIGATOIRE =====
# MySQL (serveur distant)
DATABASE_URL=mysql+pymysql://magma:YAN%40mol1234@159.89.13.54:3306/ecolearnai_db?charset=utf8mb4

# JWT (securite tokens)
SECRET_KEY=<cle-secrete-aleatoire-256-bits>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Chiffrement RGPD (Fernet / AES-128-CBC)
# Generer avec : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=<cle-fernet-generee>

# ===== SERVICES EXTERNES =====
# OpenAI (generation de contenu IA)
OPENAI_API_KEY=sk-...

# Moko Checkout / FreshPay (paiement carte bancaire)
MOKO_API_KEY=<votre-cle-moko>
MOKO_API_SECRET=<votre-secret-moko>
MOKO_BASE_URL=https://test.card.gofreshpay.com
MOKO_CALLBACK_URL=https://votre-domaine.com/api/payments/moko/callback

# MGT-SMS (envoi de SMS)
SMS_API_URL=https://api.magictech-sms.com/send-sms
SMS_API_KEY=<votre-cle-sms>
SMS_SENDER_ID=EcoLearnAI

# Email SMTP (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=ylangwana@gmail.com
EMAIL_HOST_PASSWORD=<mot-de-passe-application-gmail>
EMAIL_FROM_NAME=EcoLearn AI
OTP_EXPIRY_MINUTES=10

# ===== REDIS (cache) =====
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=EcoLearn@Redis2026
REDIS_MAX_CONNECTIONS=50

# ===== BACKUP (replication cron) =====
BACKUP_DATABASE_URL=mysql+pymysql://magma:YAN%40mol1234@159.89.13.55:3306/ecolearnai_db_backup?charset=utf8mb4
BACKUP_CRON_HOUR=1
BACKUP_CRON_MINUTE=0
BACKUP_ENABLED=true

# ===== MONITORING =====
MONITORING_ENABLED=true
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=EcoLearn@Grafana2026
```

> **IMPORTANT** : Generez la cle de chiffrement Fernet avec cette commande :
> ```bash
> python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
> ```

### Etape 3 : Lancer avec Docker Compose

```bash
# Construire et demarrer tous les services
docker compose up --build -d

# Verifier que les services fonctionnent
docker compose ps

# Consulter les logs
docker compose logs -f backend
```

### Etape 4 : Verifier le deploiement

```bash
# Health check
curl http://localhost:8000/health
# Reponse attendue : {"status":"healthy","cache":"up","backup_enabled":true}

# Health check detaille (tous les composants)
curl http://localhost:8000/api/monitoring/health

# Info API
curl http://localhost:8000/
# Reponse attendue : {"name":"EcoLearn AI","version":"1.4.0","status":"running","docs":"/docs"}
```

### Services deployes

| Service          | Port  | URL                      | Description                      |
|------------------|-------|--------------------------|----------------------------------|
| Backend API      | 8000  | http://localhost:8000    | FastAPI (Python)                 |
| AI Service       | 5000  | http://localhost:5000    | Flask + OpenAI GPT               |
| Redis            | 6379  | localhost:6379           | Cache + Rate Limiting            |
| MySQL            | 3306  | 159.89.13.54:3306       | Base de donnees (serveur distant)|
| MySQL Backup     | 3306  | 159.89.13.55:3306       | Base de backup (replication cron)|
| Prometheus       | 9090  | http://localhost:9090    | Collecte de metriques            |
| Grafana          | 3000  | http://localhost:3000    | Dashboards visuels               |
| Node Exporter    | 9100  | localhost:9100           | Metriques OS                     |
| Redis Exporter   | 9121  | localhost:9121           | Metriques Redis                  |
| MySQL Exporter   | 9104  | localhost:9104           | Metriques MySQL                  |

### Commandes utiles

```bash
# Arreter les services
docker compose down

# Reconstruire apres modification du code
docker compose up --build -d

# Reinitialiser la base de donnees
docker compose down -v && docker compose up --build -d

# Voir les logs en temps reel
docker compose logs -f backend ai-service
```

---

## 2. Architecture & Technologies

```
Client (Frontend)
      |
      v
  [FastAPI Backend :8000]  --->  [Flask AI Service :5000]  --->  OpenAI GPT
      |         |
      |         +--- [Redis :6379] (Cache, Rate Limiting, OTP anti brute-force)
      v
  [MySQL NDB Cluster :3306]  --->  [MySQL Backup :3306] (cron 01:00 UTC)
      |
      +--- Moko Checkout (paiement carte)
      +--- MGT-SMS (envoi SMS)
      +--- Gmail SMTP (envoi emails)

  [Prometheus :9090]  --->  [Grafana :3000] (Dashboards visuels)
      |
      +--- Backend /metrics (FastAPI Instrumentator)
      +--- Redis Exporter :9121
      +--- MySQL Exporter :9104
      +--- Node Exporter :9100 (OS)
```

| Composant       | Technologie                         |
|-----------------|-------------------------------------|
| Backend API     | FastAPI (Python 3.12)               |
| Base de donnees | MySQL 8.0 (NDB Cluster)             |
| ORM             | SQLAlchemy 2.x                      |
| Cache           | Redis 7.2 (256 Mo, LRU eviction)   |
| Auth            | JWT (python-jose) + bcrypt          |
| Chiffrement     | Fernet (AES-128-CBC + HMAC-SHA256)  |
| Service IA      | Flask + OpenAI GPT                  |
| Paiement carte  | Moko Checkout / FreshPay            |
| SMS             | MGT-SMS API                         |
| Email           | Gmail SMTP (SSL, port 465)          |
| Monitoring      | Prometheus + Grafana + Exporters    |
| Backup cron     | APScheduler (replication quotidienne)|
| Conteneurisation| Docker + Docker Compose (8 services)|

---

## 3. Authentification (JWT)

L'API utilise des tokens **JWT Bearer** pour l'authentification.

### Obtenir un token

Appeler `POST /api/auth/login` avec les identifiants. Le token retourne doit etre inclus dans chaque requete protegee.

### Inclure le token

Ajouter le header `Authorization` a chaque requete :

```
Authorization: Bearer <votre-token-jwt>
```

### Duree de vie

Le token expire apres **30 minutes** par defaut (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

### Endpoints publics (sans token)

| Endpoint                       | Description                      |
|--------------------------------|----------------------------------|
| `GET /`                        | Informations de l'API            |
| `GET /health`                  | Health check simple              |
| `GET /metrics`                 | Metriques Prometheus             |
| `GET /redoc`                   | Documentation ReDoc              |
| `GET /api/monitoring/health`   | Health check detaille            |
| `POST /api/auth/register`      | Inscription                      |
| `POST /api/auth/verify-sms`    | Verification SMS                 |
| `POST /api/auth/resend-otp`    | Renvoi OTP                       |
| `POST /api/auth/login`         | Connexion                        |
| `GET /api/subscriptions/plans` | Liste des plans                  |
| `POST /api/payments/moko/callback` | Callback Moko (serveur) |

Tous les autres endpoints necessitent le header `Authorization: Bearer <token>`.

---

## 4. Flux d'inscription complet

Le flux d'inscription se deroule en 3 etapes obligatoires :

```
1. POST /api/auth/register     -->  Cree le compte + envoie OTP par SMS et Email
                                    (consentement RGPD obligatoire)
       |
       v
2. POST /api/auth/verify-sms   -->  L'utilisateur saisit le code OTP recu
                                    (par SMS ou Email, meme code)
                                    (active le compte si code correct)
       |
       v
3. POST /api/auth/login        -->  Connexion et obtention du JWT token
                                    (refuse si compte non verifie)
```

**Regles :**
- L'utilisateur doit accepter le consentement RGPD (`gdpr_consent: true`)
- Le mot de passe doit contenir min. 8 caracteres, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractere special
- L'utilisateur doit avoir au moins 13 ans
- Le code OTP expire apres 10 minutes
- Le meme code OTP est envoye par **SMS** et par **Email** (l'utilisateur peut utiliser l'un ou l'autre)

---

## 5. Endpoints API

---

### 5.1 Root & Health

#### `GET /`

Informations generales de l'API.

**Auth** : Non requise

**Reponse** `200 OK` :
```json
{
  "name": "EcoLearn AI",
  "version": "1.4.0",
  "status": "running",
  "docs": "/docs",
  "description": "Plateforme d'apprentissage en ligne intelligente et ecologique"
}
```

---

#### `GET /health`

Verification de l'etat de sante du service.

**Auth** : Non requise

**Reponse** `200 OK` :
```json
{
  "status": "healthy",
  "cache": "up",
  "backup_enabled": true
}
```

---

#### `GET /metrics`

Metriques Prometheus au format OpenMetrics (utilise par Prometheus pour le scraping).

**Auth** : Non requise

**Reponse** `200 OK` : texte au format Prometheus (compteurs HTTP, latence, etc.)

---

### 5.2 Authentification

**Prefix** : `/api/auth`

---

#### `POST /api/auth/register`

Inscription d'un nouvel utilisateur avec consentement RGPD et chiffrement des donnees sensibles.

**Auth** : Non requise

**Body** (`application/json`) :

| Champ                       | Type     | Requis | Description                                                     |
|-----------------------------|----------|--------|-----------------------------------------------------------------|
| `email`                     | string   | Oui    | Adresse email valide                                            |
| `password`                  | string   | Oui    | Min 8 car., 1 maj, 1 min, 1 chiffre, 1 special                 |
| `full_name`                 | string   | Oui    | Nom complet                                                     |
| `phone_number`              | string   | Oui    | Format E.164 (ex: `+243898900119`)                              |
| `date_of_birth`             | string   | Oui    | Format `YYYY-MM-DD`, age minimum 13 ans                        |
| `gender`                    | string   | Non    | `homme`, `femme`, `autre`, `non_precise` (defaut: `non_precise`)|
| `nationality`               | string   | Non    | Nationalite (ex: `Congolaise`)                                  |
| `national_id_number`        | string   | Non    | Numero de piece d'identite (chiffre en base)                    |
| `national_id_type`          | string   | Non    | `carte_identite`, `passeport`, `permis_conduire`, `carte_sejour`|
| `address_line`              | string   | Non    | Adresse (rue et numero)                                         |
| `address_city`              | string   | Non    | Ville                                                           |
| `address_postal_code`       | string   | Non    | Code postal                                                     |
| `address_country`           | string   | Non    | Pays                                                            |
| `level`                     | string   | Non    | `debutant` (defaut), `intermediaire`, `avance`, `expert`        |
| `objectives`                | string   | Non    | Objectifs d'apprentissage                                       |
| `preferences`               | string   | Non    | Preferences pedagogiques                                       |
| `gdpr_consent`              | boolean  | **Oui**| **Doit etre `true`** pour s'inscrire                            |
| `gdpr_marketing_consent`    | boolean  | Non    | Consentement communications marketing (defaut: `false`)         |
| `gdpr_data_retention_consent`| boolean | Non    | Consentement conservation donnees (defaut: `false`)             |

**Exemple de requete :**

```json
{
  "email": "jean.dupont@email.com",
  "password": "MonMotDePasse1!",
  "full_name": "Jean Dupont",
  "phone_number": "+243898900119",
  "date_of_birth": "1990-05-15",
  "gender": "homme",
  "nationality": "Congolaise",
  "address_city": "Kinshasa",
  "address_country": "RDC",
  "gdpr_consent": true,
  "gdpr_marketing_consent": false
}
```

**Reponse** `201 Created` :
```json
{
  "message": "Inscription reussie ! Un code de verification a ete envoye par SMS et par email.",
  "user": {
    "id": "uuid",
    "email": "jean.dupont@email.com",
    "phone_number": "+243898900119",
    "full_name": "Jean Dupont",
    "gender": "homme",
    "date_of_birth": "1990-05-15",
    "nationality": "Congolaise",
    "national_id_type": null,
    "has_national_id": false,
    "address_city": "Kinshasa",
    "address_country": "RDC",
    "address_line_masked": null,
    "address_postal_code_masked": null,
    "gdpr_consent": true,
    "gdpr_consent_at": "2026-02-09T10:30:00",
    "gdpr_marketing_consent": false,
    "gdpr_data_retention_consent": false,
    "is_verified": false,
    "is_active": true,
    "level": "debutant",
    "total_xp": 0,
    "current_streak": 0,
    "..."
  },
  "sms_sent": true,
  "sms_error": null,
  "email_sent": true,
  "email_error": null,
  "verification_required": true,
  "rgpd_info": {
    "consent_recorded": true,
    "consent_date": "2026-02-09T10:30:00",
    "sensitive_data_encrypted": true,
    "encryption_method": "Fernet (AES-128-CBC + HMAC-SHA256)"
  }
}
```

**Erreurs possibles :**

| Code | Detail                                                                        |
|------|-------------------------------------------------------------------------------|
| 400  | `Un compte avec cet email existe deja.`                                       |
| 400  | `Un compte avec ce numero de telephone existe deja.`                          |
| 422  | Erreurs de validation (mot de passe, telephone, date de naissance, consent...) |

---

#### `POST /api/auth/verify-sms`

Verifier le code OTP recu par SMS ou par email pour activer le compte. Le meme code est envoye sur les deux canaux.

**Auth** : Non requise

**Body** :

| Champ   | Type   | Requis | Description                             |
|---------|--------|--------|-----------------------------------------|
| `email` | string | Oui    | Email du compte a verifier              |
| `code`  | string | Oui    | Code OTP a 6 chiffres recu par SMS ou email |

**Exemple :**
```json
{
  "email": "jean.dupont@email.com",
  "code": "482917"
}
```

**Reponse** `200 OK` :
```json
{
  "message": "Compte verifie avec succes ! Vous pouvez maintenant vous connecter.",
  "user": { "...UserResponse..." }
}
```

**Erreurs :**

| Code | Detail                                              |
|------|-----------------------------------------------------|
| 400  | `Ce compte est deja verifie.`                       |
| 400  | `Code expire. Demandez un nouveau code via /resend-otp.` |
| 400  | `Code de verification incorrect.`                   |
| 404  | `Aucun compte trouve avec cet email.`               |

---

#### `POST /api/auth/resend-otp`

Renvoyer un nouveau code OTP par SMS et par email (si expire ou non recu).

**Auth** : Non requise

**Body** :

| Champ   | Type   | Requis | Description         |
|---------|--------|--------|---------------------|
| `email` | string | Oui    | Email du compte     |

**Reponse** `200 OK` :
```json
{
  "message": "Un nouveau code de verification a ete envoye par SMS et par email.",
  "sms_sent": true,
  "sms_error": null,
  "email_sent": true,
  "email_error": null
}
```

---

#### `POST /api/auth/login`

Connexion et obtention du token JWT.

**Auth** : Non requise

**Body** (`application/x-www-form-urlencoded`) :

| Champ      | Type   | Requis | Description                  |
|------------|--------|--------|------------------------------|
| `username` | string | Oui    | **Email** de l'utilisateur   |
| `password` | string | Oui    | Mot de passe                 |

> **Note pour le frontend** : Ce endpoint utilise le format OAuth2 (`application/x-www-form-urlencoded`), pas JSON. Le champ s'appelle `username` mais c'est l'email qui doit etre envoye.

**Exemple avec fetch :**
```javascript
const formData = new URLSearchParams();
formData.append('username', 'jean.dupont@email.com');
formData.append('password', 'MonMotDePasse1!');

const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: formData,
});
```

**Reponse** `200 OK` :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "jean.dupont@email.com",
    "full_name": "Jean Dupont",
    "level": "debutant",
    "total_xp": 0,
    "is_verified": true,
    "..."
  }
}
```

**Erreurs :**

| Code | Detail                                                        |
|------|---------------------------------------------------------------|
| 401  | `Email ou mot de passe incorrect.`                            |
| 403  | `Votre compte n'est pas encore verifie...`                    |
| 403  | `Ce compte a ete desactive. Contactez le support.`            |

---

### 5.3 Utilisateurs & Profil

**Prefix** : `/api/users`
**Auth** : Bearer Token requis pour tous les endpoints

---

#### `GET /api/users/me`

Recuperer le profil complet de l'utilisateur connecte (donnees sensibles dechiffrees, adresse partiellement masquee).

**Reponse** `200 OK` :
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "jean.dupont@email.com",
  "phone_number": "+243898900119",
  "full_name": "Jean Dupont",
  "gender": "homme",
  "date_of_birth": "1990-05-15",
  "nationality": "Congolaise",
  "national_id_type": null,
  "has_national_id": false,
  "address_city": "Kinshasa",
  "address_country": "RDC",
  "address_line_masked": "12 Ru***",
  "address_postal_code_masked": "75***",
  "gdpr_consent": true,
  "gdpr_consent_at": "2026-02-09T10:30:00",
  "gdpr_marketing_consent": false,
  "gdpr_data_retention_consent": false,
  "avatar_url": null,
  "bio": null,
  "language": "fr",
  "timezone": "Europe/Paris",
  "level": "debutant",
  "objectives": null,
  "preferences": null,
  "total_xp": 150,
  "current_streak": 3,
  "longest_streak": 7,
  "last_activity_date": "2026-02-09",
  "total_learning_minutes": 45.5,
  "is_active": true,
  "is_verified": true,
  "last_login_at": "2026-02-09T10:30:00",
  "created_at": "2026-02-01T08:00:00",
  "updated_at": "2026-02-09T10:30:00"
}
```

> **Note RGPD** : L'adresse est partiellement masquee (`12 Ru***`, `75***`). Le numero de piece d'identite n'est jamais retourne (seul `has_national_id: true/false` est indique). Pour un export complet, utiliser `GET /api/users/me/data-export`.

---

#### `PUT /api/users/me`

Mettre a jour le profil. Les donnees sensibles sont automatiquement re-chiffrees.

**Body** (tous les champs sont optionnels, envoyer uniquement ceux a modifier) :

| Champ                  | Type   | Description                                            |
|------------------------|--------|--------------------------------------------------------|
| `full_name`            | string | Nom complet                                            |
| `gender`               | string | `homme`, `femme`, `autre`, `non_precise`               |
| `date_of_birth`        | string | Format `YYYY-MM-DD` (re-chiffre avant stockage)        |
| `nationality`          | string | Nationalite (re-chiffree)                              |
| `national_id_number`   | string | Numero de piece (re-chiffre)                           |
| `national_id_type`     | string | Type de piece d'identite                               |
| `address_line`         | string | Adresse rue (re-chiffree)                              |
| `address_city`         | string | Ville (re-chiffree)                                    |
| `address_postal_code`  | string | Code postal (re-chiffre)                               |
| `address_country`      | string | Pays (re-chiffre)                                      |
| `avatar_url`           | string | URL de l'avatar                                        |
| `bio`                  | string | Biographie                                             |
| `language`             | string | Langue (ex: `fr`, `en`)                                |
| `timezone`             | string | Fuseau horaire (ex: `Europe/Paris`)                    |
| `level`                | string | `debutant`, `intermediaire`, `avance`, `expert`        |
| `objectives`           | string | Objectifs d'apprentissage                              |
| `preferences`          | string | Preferences pedagogiques                               |

**Exemple :**
```json
{
  "bio": "Passionnee d'ecologie et de technologie",
  "address_city": "Lubumbashi",
  "language": "fr"
}
```

**Reponse** `200 OK` : objet `UserResponse` mis a jour.

---

#### `PUT /api/users/me/password`

Changer le mot de passe.

**Body** :

| Champ              | Type   | Requis | Description                                     |
|--------------------|--------|--------|-------------------------------------------------|
| `current_password` | string | Oui    | Mot de passe actuel                             |
| `new_password`     | string | Oui    | Nouveau mot de passe (memes regles que register)|

**Exemple :**
```json
{
  "current_password": "MonMotDePasse1!",
  "new_password": "NouveauMDP2@2026"
}
```

**Reponse** `200 OK` :
```json
{
  "message": "Mot de passe modifie avec succes."
}
```

**Erreurs :**

| Code | Detail                                                       |
|------|--------------------------------------------------------------|
| 400  | `Le mot de passe actuel est incorrect.`                      |
| 400  | `Le nouveau mot de passe doit etre different de l'ancien.`   |
| 422  | Validation (longueur, complexite)                            |

---

#### `GET /api/users/me/progression`

Resume complet de la progression de l'utilisateur.

**Reponse** `200 OK` :
```json
{
  "user_id": "uuid",
  "full_name": "Jean Dupont",
  "level": "intermediaire",
  "total_xp": 1250,
  "xp_to_next_level": 750,
  "current_streak": 5,
  "longest_streak": 12,
  "total_paths": 3,
  "active_paths": 1,
  "completed_paths": 2,
  "abandoned_paths": 0,
  "total_sessions": 15,
  "completed_sessions": 12,
  "average_score": 78.5,
  "best_score": 95.0,
  "total_learning_minutes": 450.0,
  "total_learning_hours": 7.5,
  "paths": [
    {
      "path_id": "uuid",
      "title": "Python pour debutants",
      "subject": "python",
      "difficulty": "debutant",
      "total_sessions": 5,
      "completed_sessions": 5,
      "progress_percent": 100.0,
      "status": "termine",
      "average_score": 85.0,
      "total_duration_minutes": 150.0,
      "created_at": "2026-01-15T10:00:00"
    }
  ],
  "total_achievements_unlocked": 5,
  "total_achievements_available": 20,
  "achievements": [
    {
      "id": "uuid",
      "code": "first_session",
      "name": "Premiere session",
      "description": "Terminer sa premiere session",
      "icon": "star",
      "category": "apprentissage",
      "xp_reward": 50,
      "unlocked_at": "2026-01-15T12:00:00"
    }
  ]
}
```

---

#### `GET /api/users/me/achievements`

Lister tous les badges (debloques et disponibles).

**Reponse** `200 OK` : Liste d'objets `AchievementResponse`

```json
[
  {
    "id": "uuid",
    "code": "streak_7",
    "name": "Une semaine de feu",
    "description": "Maintenir un streak de 7 jours",
    "icon": "fire",
    "category": "engagement",
    "xp_reward": 100,
    "unlocked_at": "2026-02-05T09:00:00"
  },
  {
    "id": "uuid",
    "code": "streak_30",
    "name": "Un mois incroyable",
    "description": "Maintenir un streak de 30 jours",
    "icon": "trophy",
    "category": "engagement",
    "xp_reward": 500,
    "unlocked_at": null
  }
]
```

> **Astuce frontend** : Si `unlocked_at` est `null`, le badge n'est pas encore debloque. Afficher les badges non debloques en grise.

---

#### `PUT /api/users/me/deactivate`

Desactiver le compte (l'utilisateur ne peut plus se connecter).

**Reponse** `200 OK` :
```json
{
  "message": "Compte desactive avec succes. Contactez le support pour le reactiver."
}
```

---

#### `DELETE /api/users/me`

Supprimer definitivement le compte et toutes les donnees (RGPD Article 17).

**Reponse** `200 OK` :
```json
{
  "message": "Compte et toutes les donnees associees supprimes definitivement.",
  "rgpd": "Droit a l'effacement exerce avec succes (Article 17 RGPD)."
}
```

> **ATTENTION** : Cette action est **irreversible**. Afficher un dialogue de confirmation cote frontend.

---

### 5.4 RGPD / GDPR

**Prefix** : `/api/users`
**Auth** : Bearer Token requis

Ces endpoints implementent les droits fondamentaux du RGPD.

---

#### `GET /api/users/me/data-export`

**Droit a la portabilite** (Article 20 RGPD).

Export complet de TOUTES les donnees personnelles, entierement dechiffrees (y compris l'adresse non masquee et le numero de piece d'identite).

**Reponse** `200 OK` :
```json
{
  "id": "uuid",
  "email": "jean.dupont@email.com",
  "phone_number": "+243898900119",
  "full_name": "Jean Dupont",
  "gender": "homme",
  "date_of_birth": "1990-05-15",
  "nationality": "Congolaise",
  "national_id_type": "carte_identite",
  "national_id_number": "AB1234567",
  "address_line": "12 Rue de la Paix",
  "address_city": "Kinshasa",
  "address_postal_code": "75001",
  "address_country": "RDC",
  "gdpr_consent": true,
  "gdpr_consent_at": "2026-02-09T10:30:00",
  "gdpr_marketing_consent": false,
  "gdpr_data_retention_consent": false,
  "avatar_url": null,
  "bio": "...",
  "language": "fr",
  "timezone": "Europe/Paris",
  "level": "intermediaire",
  "total_xp": 1250,
  "..."
}
```

> **Frontend** : Proposer un bouton "Telecharger mes donnees" qui appelle cet endpoint et genere un fichier JSON telecharable.

---

#### `PUT /api/users/me/gdpr-consent`

**Gestion des consentements** (Article 7 RGPD).

Modifier les consentements facultatifs (le consentement principal ne peut etre retire qu'en supprimant le compte).

**Body** :

| Champ                         | Type    | Requis | Description                   |
|-------------------------------|---------|--------|-------------------------------|
| `gdpr_marketing_consent`      | boolean | Non    | Communications marketing      |
| `gdpr_data_retention_consent` | boolean | Non    | Conservation etendue          |

**Exemple :**
```json
{
  "gdpr_marketing_consent": true,
  "gdpr_data_retention_consent": false
}
```

**Reponse** `200 OK` :
```json
{
  "message": "Consentements RGPD mis a jour avec succes.",
  "changes": {
    "marketing": true,
    "data_retention": false
  },
  "updated_at": "2026-02-09T11:00:00"
}
```

---

#### `GET /api/users/me/privacy-info`

**Droit a l'information** (Articles 13-14 RGPD).

Retourne un document structure expliquant quelles donnees sont collectees, pourquoi, comment elles sont protegees, et les droits de l'utilisateur.

**Reponse** `200 OK` :
```json
{
  "responsable_traitement": {
    "nom": "EcoLearn AI",
    "contact": "dpo@ecolearn-ai.com"
  },
  "donnees_collectees": {
    "obligatoires": [
      {"champ": "email", "finalite": "Identification et communication", "chiffre": false},
      {"champ": "mot_de_passe", "finalite": "Authentification", "chiffre": true, "methode": "bcrypt"},
      {"champ": "date_de_naissance", "finalite": "Verification d'age", "chiffre": true, "methode": "Fernet AES-128-CBC"}
    ],
    "facultatives": [
      {"champ": "nationalite", "finalite": "Adaptation des contenus", "chiffre": true},
      {"champ": "adresse", "finalite": "Facturation", "chiffre": true}
    ]
  },
  "protection_donnees": {
    "chiffrement": "Fernet (AES-128-CBC + HMAC-SHA256)",
    "hachage_mot_de_passe": "bcrypt",
    "transport": "TLS 1.2+",
    "donnees_chiffrees_en_base": ["date_de_naissance", "nationalite", "numero_piece_identite", "adresse_rue", "ville", "code_postal", "pays"]
  },
  "droits_utilisateur": {
    "acces": "GET /api/users/me",
    "portabilite": "GET /api/users/me/data-export",
    "rectification": "PUT /api/users/me",
    "effacement": "DELETE /api/users/me",
    "consentement": "PUT /api/users/me/gdpr-consent",
    "information": "GET /api/users/me/privacy-info"
  },
  "consentements_actuels": {
    "traitement_donnees": true,
    "date_consentement": "2026-02-09T10:30:00",
    "marketing": false,
    "conservation_donnees": false
  },
  "duree_conservation": {
    "compte_actif": "Donnees conservees tant que le compte est actif",
    "compte_desactive": "Donnees anonymisees apres 3 ans d'inactivite",
    "suppression": "Effacement immediat et irreversible sur demande"
  }
}
```

> **Frontend** : Utiliser ces donnees pour construire une page "Politique de confidentialite" dynamique et personnalisee.

---

### 5.5 Abonnements

**Prefix** : `/api/subscriptions`

---

#### `GET /api/subscriptions/plans`

Lister les plans d'abonnement disponibles. Les plans sont lus depuis la base de donnees (configurables par l'administrateur).

**Auth** : Non requise

**Reponse** `200 OK` :
```json
{
  "plans": [
    {
      "code": "mensuel",
      "name": "Abonnement Mensuel",
      "description": "Acces complet pendant 30 jours",
      "price": 9.99,
      "currency": "USD",
      "duration_days": 30,
      "features": null
    },
    {
      "code": "annuel",
      "name": "Abonnement Annuel",
      "description": "Acces complet pendant 1 an - Economisez 30%",
      "price": 89.99,
      "currency": "USD",
      "duration_days": 365,
      "features": null
    }
  ],
  "payment_methods": [
    {"code": "carte_bancaire", "label": "Carte bancaire (Visa, Mastercard)", "provider": "Umoja / FreshPay"},
    {"code": "mobile_money", "label": "Mobile Money (Orange, MTN, Airtel, Wave)"}
  ]
}
```

> **Note** : Les plans sont configurables par l'administrateur via `POST /api/admin/plans`. Si aucun plan n'existe en base, des valeurs par defaut sont retournees.
```

---

#### `POST /api/subscriptions/subscribe`

Souscrire a un abonnement.

**Auth** : Bearer Token requis

**Body** :

| Champ            | Type   | Requis | Description                                  |
|------------------|--------|--------|----------------------------------------------|
| `plan`           | string | Oui    | `mensuel` ou `annuel`                        |
| `payment_method` | string | Oui    | `carte_bancaire` ou `mobile_money`           |

**Exemple :**
```json
{
  "plan": "mensuel",
  "payment_method": "carte_bancaire"
}
```

**Reponse (carte bancaire)** `200 OK` :
```json
{
  "message": "Paiement initie. Completez le paiement via le lien ci-dessous.",
  "payment_method": "carte_bancaire",
  "status": "pending",
  "payment_url": "https://pay.gofreshpay.com/checkout/abc123...",
  "transaction_uuid": "txn-uuid-...",
  "subscription": { "...SubscriptionResponse..." },
  "payment": { "...PaymentResponse..." }
}
```

> **Frontend (carte bancaire)** : Rediriger l'utilisateur vers `payment_url`. Apres le paiement, Moko enverra un callback au backend. Utiliser `GET /api/payments/{payment_id}/status` pour interroger le statut.

**Reponse (mobile money)** `200 OK` :
```json
{
  "message": "Abonnement mensuel active avec succes !",
  "payment_method": "mobile_money",
  "status": "completed",
  "subscription": { "...SubscriptionResponse..." },
  "payment": { "...PaymentResponse..." }
}
```

---

#### `GET /api/subscriptions/my`

Lister mes abonnements.

**Auth** : Bearer Token requis

**Reponse** `200 OK` :
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "plan": "mensuel",
    "price": 9.99,
    "currency": "USD",
    "is_active": true,
    "start_date": "2026-02-09T10:30:00",
    "end_date": "2026-03-11T10:30:00",
    "auto_renew": true,
    "created_at": "2026-02-09T10:30:00"
  }
]
```

---

### 5.6 Paiements & Factures

**Prefix** : `/api/payments`

---

#### `GET /api/payments/my`

Lister tous mes paiements et factures.

**Auth** : Bearer Token requis

**Reponse** `200 OK` :
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "subscription_id": "uuid",
    "amount": 9.99,
    "currency": "USD",
    "payment_method": "carte_bancaire",
    "status": "completed",
    "transaction_ref": "TXN-20260209-ABC123",
    "invoice_number": "INV-20260209-001",
    "invoice_details": "Abonnement mensuel EcoLearn AI...",
    "moko_transaction_uuid": "txn-uuid-...",
    "moko_payment_url": null,
    "paid_at": "2026-02-09T10:35:00",
    "created_at": "2026-02-09T10:30:00"
  }
]
```

---

#### `GET /api/payments/{payment_id}/invoice`

Consulter une facture specifique.

**Auth** : Bearer Token requis

**Parametres URL** :

| Parametre    | Type   | Description          |
|--------------|--------|----------------------|
| `payment_id` | UUID   | ID du paiement       |

**Reponse** `200 OK` :
```json
{
  "invoice_number": "INV-20260209-001",
  "amount": 9.99,
  "currency": "USD",
  "payment_method": "carte_bancaire",
  "status": "completed",
  "transaction_ref": "TXN-20260209-ABC123",
  "moko_transaction_uuid": "txn-uuid-...",
  "paid_at": "2026-02-09T10:35:00",
  "invoice_details": "Facture EcoLearn AI\n..."
}
```

---

#### `GET /api/payments/{payment_id}/status`

Verifier le statut d'un paiement (utile pour le polling apres paiement carte).

**Auth** : Bearer Token requis

**Reponse** `200 OK` :
```json
{
  "payment_id": "uuid",
  "status": "completed",
  "payment_method": "carte_bancaire",
  "moko_transaction_uuid": "txn-uuid-...",
  "paid_at": "2026-02-09T10:35:00",
  "subscription_active": true
}
```

> **Frontend** : Apres la redirection Moko, interroger ce endpoint toutes les 3 secondes (polling) jusqu'a ce que `status` soit `completed` ou `failed`.

**Valeurs de `status`** :

| Statut      | Description                         |
|-------------|-------------------------------------|
| `pending`   | En attente de paiement              |
| `completed` | Paiement reussi, abonnement actif   |
| `failed`    | Paiement echoue                     |

---

#### `POST /api/payments/moko/callback`

Webhook appele par Moko Checkout apres traitement du paiement.

**Auth** : Non requise (verifie par signature HMAC)

> **Note** : Ce endpoint est appele directement par le serveur Moko, pas par le frontend. Il ne faut pas l'appeler manuellement.

---

### 5.7 Apprentissage

**Prefix** : `/api/learning`
**Auth** : Bearer Token requis pour tous les endpoints

> **Abonnement requis** : Les endpoints `POST /api/learning/paths` et `POST /api/learning/sessions` necessitent un abonnement actif. Les utilisateurs sans abonnement recevront une erreur `403 Forbidden`. Les administrateurs sont exemptes. Consultez la section [Abonnements](#55-abonnements) pour souscrire.

---

#### `POST /api/learning/paths`

Creer un nouveau parcours d'apprentissage.

**Auth** : Bearer Token requis + **Abonnement actif requis** (admins exemptes)

**Body** :

| Champ            | Type   | Requis | Description                                    |
|------------------|--------|--------|------------------------------------------------|
| `title`          | string | Oui    | Titre du parcours                              |
| `subject`        | string | Oui    | Sujet (ex: `python`, `javascript`, `ecologie`) |
| `description`    | string | Non    | Description detaillee                          |
| `difficulty`     | string | Non    | `debutant`, `intermediaire`, `avance`, `expert` (defaut: niveau de l'utilisateur) |
| `total_sessions` | int    | Non    | Nombre de sessions prevues (defaut: 5)         |

**Exemple :**
```json
{
  "title": "Python pour debutants",
  "subject": "python",
  "description": "Apprendre les bases de Python",
  "difficulty": "debutant",
  "total_sessions": 8
}
```

**Reponse** `201 Created` :
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Python pour debutants",
  "description": "Apprendre les bases de Python",
  "subject": "python",
  "difficulty": "debutant",
  "total_sessions": 8,
  "completed_sessions": 0,
  "progress_percent": 0.0,
  "status": "en_cours",
  "created_at": "2026-02-09T10:00:00",
  "updated_at": "2026-02-09T10:00:00"
}
```

**Erreurs possibles :**

| Code | Detail                                                                              |
|------|-------------------------------------------------------------------------------------|
| 403  | `Abonnement requis. Vous devez souscrire a un abonnement actif pour creer des parcours et generer des cours.` |

---

#### `GET /api/learning/paths`

Lister mes parcours d'apprentissage.

**Reponse** `200 OK` : Liste d'objets `LearningPathResponse`

---

#### `GET /api/learning/paths/{path_id}`

Recuperer un parcours specifique.

**Parametres URL** :

| Parametre | Type | Description     |
|-----------|------|-----------------|
| `path_id` | UUID | ID du parcours  |

**Reponse** `200 OK` : objet `LearningPathResponse`

---

#### `POST /api/learning/sessions`

Demarrer une session d'apprentissage. Le contenu est genere par l'IA (GPT).

**Auth** : Bearer Token requis + **Abonnement actif requis** (admins exemptes)

**Body** :

| Champ              | Type | Requis | Description                    |
|--------------------|------|--------|--------------------------------|
| `learning_path_id` | UUID | Oui    | ID du parcours parent          |
| `title`            | string | Oui  | Titre de la session            |

**Exemple :**
```json
{
  "learning_path_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Variables et types de donnees"
}
```

**Reponse** `201 Created` :
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "learning_path_id": "uuid",
  "title": "Variables et types de donnees",
  "content": "# Variables et types de donnees en Python\n\nDans cette lecon, nous allons decouvrir...",
  "duration_minutes": 0.0,
  "score": null,
  "session_number": 1,
  "status": "en_cours",
  "started_at": "2026-02-09T10:00:00",
  "completed_at": null,
  "created_at": "2026-02-09T10:00:00"
}
```

> **Frontend** : Le champ `content` contient le contenu pedagogique genere par l'IA au format texte/Markdown. L'afficher dans l'interface d'apprentissage.

**Erreurs possibles :**

| Code | Detail                                                                              |
|------|-------------------------------------------------------------------------------------|
| 403  | `Abonnement requis. Vous devez souscrire a un abonnement actif pour creer des parcours et generer des cours.` |

---

#### `PUT /api/learning/sessions/{session_id}/complete`

Terminer une session. Declenche automatiquement :
1. Calcul de l'empreinte carbone
2. Attribution de XP
3. Mise a jour du streak
4. Verification de completion du parcours
5. Montee de niveau automatique
6. Verification et deblocage de badges
7. Declenchement de compensation ecologique si seuil atteint

**Parametres URL** :

| Parametre    | Type | Description      |
|--------------|------|------------------|
| `session_id` | UUID | ID de la session |

**Body** :

| Champ              | Type  | Requis | Description                       |
|--------------------|-------|--------|-----------------------------------|
| `score`            | float | Non    | Score obtenu (0-100)              |
| `duration_minutes` | float | Non    | Duree en minutes (calcule auto si absent) |

**Exemple :**
```json
{
  "score": 85.0,
  "duration_minutes": 25.5
}
```

**Reponse** `200 OK` :
```json
{
  "message": "Session terminee avec succes !",
  "session": { "...SessionResponse..." },
  "carbon_footprint": {
    "energy_kwh": 0.085,
    "carbon_kg": 0.040,
    "server_region": "europe-west"
  },
  "progression": {
    "xp_earned": 85,
    "total_xp": 1335,
    "level": "intermediaire",
    "level_up": false,
    "streak": 6,
    "streak_continued": true,
    "new_badges": [
      {
        "name": "Premiere semaine",
        "description": "Maintenir un streak de 7 jours",
        "icon": "fire",
        "xp_reward": 100
      }
    ],
    "path_completed": null
  },
  "eco_compensation": null
}
```

**Quand un parcours est complete :**
```json
{
  "progression": {
    "...": "...",
    "path_completed": {
      "title": "Python pour debutants",
      "message": "Felicitations ! Vous avez termine le parcours 'Python pour debutants' !"
    }
  }
}
```

**Quand une compensation ecologique est declenchee (seuil CO2 atteint) :**
```json
{
  "eco_compensation": {
    "trees_planted": 1,
    "co2_compensated_kg": 10.5,
    "message": "Bravo ! 1 arbre(s) plante(s) pour compenser 10.50 kg de CO2."
  }
}
```

---

#### `GET /api/learning/sessions`

Lister toutes mes sessions.

**Reponse** `200 OK` : Liste d'objets `SessionResponse`

---

### 5.8 Empreinte Carbone

**Prefix** : `/api/carbon`
**Auth** : Bearer Token requis

---

#### `GET /api/carbon/summary`

Resume de l'empreinte carbone.

**Reponse** `200 OK` :
```json
{
  "total_sessions": 15,
  "total_duration_minutes": 450.0,
  "total_energy_kwh": 1.5,
  "total_carbon_kg": 0.7125,
  "total_trees_planted": 0,
  "total_co2_compensated_kg": 0.0,
  "compensation_threshold_kg": 10.0,
  "next_compensation_in_kg": 9.2875
}
```

---

#### `GET /api/carbon/footprints`

Lister les empreintes carbone par session.

**Reponse** `200 OK` :
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "session_id": "uuid",
    "duration_minutes": 25.5,
    "energy_kwh": 0.085,
    "carbon_kg": 0.040,
    "server_region": "europe-west",
    "carbon_factor": 0.475,
    "created_at": "2026-02-09T10:30:00"
  }
]
```

---

#### `GET /api/carbon/compensations`

Lister les actions de compensation ecologique.

**Reponse** `200 OK` :
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "trees_planted": 1,
    "co2_compensated_kg": 10.5,
    "partner_name": "EcoTree",
    "partner_reference": "ECO-2026-001",
    "status": "confirmed",
    "notes": "Compensation automatique - seuil atteint",
    "triggered_at": "2026-02-09T10:00:00",
    "created_at": "2026-02-09T10:00:00"
  }
]
```

---

### 5.9 Tableau de Bord

**Prefix** : `/api/dashboard`
**Auth** : Bearer Token requis

---

#### `GET /api/dashboard/`

Tableau de bord interactif regroupant toutes les statistiques.

**Reponse** `200 OK` :
```json
{
  "total_learning_paths": 3,
  "active_learning_paths": 1,
  "completed_learning_paths": 2,
  "total_sessions": 15,
  "completed_sessions": 12,
  "average_score": 78.5,
  "total_learning_hours": 7.5,
  "total_xp": 1250,
  "level": "intermediaire",
  "current_streak": 5,
  "longest_streak": 12,
  "achievements_unlocked": 5,
  "carbon_summary": {
    "total_sessions": 12,
    "total_duration_minutes": 450.0,
    "total_energy_kwh": 1.5,
    "total_carbon_kg": 0.7125,
    "total_trees_planted": 0,
    "total_co2_compensated_kg": 0.0,
    "compensation_threshold_kg": 10.0,
    "next_compensation_in_kg": 9.2875
  },
  "compensations": []
}
```

> **Frontend** : Cet endpoint est ideal pour la page d'accueil / dashboard. Il regroupe pedagogie, gamification, et impact ecologique en un seul appel.

---

### 5.10 Administration

**Prefix** : `/api/admin`
**Auth** : Bearer Token avec role `admin` ou `super_admin` (sauf `seed-admin`)

> **Roles** : `user` (defaut), `admin` (gestion), `super_admin` (tous les droits, y compris la gestion des roles).

---

#### `POST /api/admin/seed-admin`

Creer le premier super administrateur. **Ne fonctionne qu'une seule fois** : si un admin existe deja, retourne une erreur.

**Auth** : Non requise (initialisation uniquement)

**Reponse** `200 OK` :
```json
{
  "message": "Super administrateur cree avec succes.",
  "email": "admin@ecolearnai.com",
  "password": "Admin@2026!",
  "role": "super_admin",
  "warning": "Changez le mot de passe immediatement apres la premiere connexion !"
}
```

> **IMPORTANT** : Apres la creation, connectez-vous avec ces identifiants et changez le mot de passe via `PUT /api/users/me/password`.

---

#### `POST /api/admin/plans`

Creer un nouveau plan d'abonnement.

**Auth** : Admin requis

**Body** :

| Champ                  | Type    | Requis | Description                                       |
|------------------------|---------|--------|---------------------------------------------------|
| `code`                 | string  | Oui    | Code unique (ex: `mensuel`, `trimestriel`)         |
| `name`                 | string  | Oui    | Nom affiche (ex: `Abonnement Mensuel`)             |
| `description`          | string  | Non    | Description du plan                                |
| `price`                | float   | Oui    | Prix (>= 0)                                       |
| `currency`             | string  | Non    | Devise (defaut: `USD`)                             |
| `duration_days`        | int     | Oui    | Duree en jours (>= 1)                              |
| `is_active`            | boolean | Non    | Disponible a la vente (defaut: `true`)             |
| `features`             | string  | Non    | Fonctionnalites incluses (JSON libre)              |
| `max_sessions_per_day` | int     | Non    | Limite de sessions par jour (`null` = illimite)    |
| `sort_order`           | int     | Non    | Ordre d'affichage (defaut: 0)                      |

**Exemple** :
```json
{
  "code": "mensuel",
  "name": "Abonnement Mensuel",
  "description": "Acces complet a tous les parcours pendant 30 jours",
  "price": 9.99,
  "currency": "USD",
  "duration_days": 30,
  "is_active": true,
  "sort_order": 1
}
```

**Reponse** `201 Created` :
```json
{
  "id": "uuid",
  "code": "mensuel",
  "name": "Abonnement Mensuel",
  "description": "Acces complet a tous les parcours pendant 30 jours",
  "price": 9.99,
  "currency": "USD",
  "duration_days": 30,
  "is_active": true,
  "features": null,
  "max_sessions_per_day": null,
  "sort_order": 1,
  "created_at": "2026-02-09T10:00:00",
  "updated_at": "2026-02-09T10:00:00"
}
```

---

#### `GET /api/admin/plans`

Lister tous les plans d'abonnement (actifs et inactifs).

**Auth** : Admin requis

**Query params** :

| Parametre          | Type    | Description                            |
|--------------------|---------|----------------------------------------|
| `include_inactive` | boolean | Inclure les plans desactives (defaut: false) |

**Reponse** `200 OK` : Liste d'objets `PlanResponse`

---

#### `GET /api/admin/plans/{plan_id}`

Recuperer un plan specifique.

**Auth** : Admin requis

**Reponse** `200 OK` : objet `PlanResponse`

---

#### `PUT /api/admin/plans/{plan_id}`

Modifier un plan d'abonnement (prix, duree, nom, etc.).

**Auth** : Admin requis

**Body** (tous les champs sont optionnels) :

| Champ                  | Type    | Description                           |
|------------------------|---------|---------------------------------------|
| `name`                 | string  | Nouveau nom                           |
| `description`          | string  | Nouvelle description                  |
| `price`                | float   | Nouveau prix                          |
| `currency`             | string  | Nouvelle devise                       |
| `duration_days`        | int     | Nouvelle duree                        |
| `is_active`            | boolean | Activer/desactiver                    |
| `features`             | string  | Nouvelles fonctionnalites             |
| `max_sessions_per_day` | int     | Nouvelle limite                       |
| `sort_order`           | int     | Nouvel ordre                          |

**Exemple (changer le prix mensuel)** :
```json
{
  "price": 12.99
}
```

**Reponse** `200 OK` : objet `PlanResponse` mis a jour

---

#### `DELETE /api/admin/plans/{plan_id}`

Supprimer un plan d'abonnement. Si des abonnements actifs utilisent ce plan, il est **desactive** au lieu d'etre supprime.

**Auth** : Admin requis

**Reponse** `200 OK` :
```json
{
  "message": "Plan desactive (encore 5 abonnement(s) actif(s)).",
  "action": "deactivated"
}
```

ou :

```json
{
  "message": "Plan supprime definitivement.",
  "action": "deleted"
}
```

---

#### `GET /api/admin/users`

Lister les utilisateurs avec pagination et filtres.

**Auth** : Admin requis

**Query params** :

| Parametre   | Type    | Description                                        |
|-------------|---------|----------------------------------------------------|
| `page`      | int     | Numero de page (defaut: 1)                         |
| `per_page`  | int     | Resultats par page (defaut: 20, max: 100)          |
| `search`    | string  | Rechercher par nom ou email                        |
| `role`      | string  | Filtrer par role (`user`, `admin`, `super_admin`)  |
| `is_active` | boolean | Filtrer par statut actif                           |

**Exemple** : `GET /api/admin/users?page=1&per_page=10&search=dupont&role=user`

**Reponse** `200 OK` :
```json
{
  "total": 150,
  "page": 1,
  "per_page": 10,
  "users": [
    {
      "id": "uuid",
      "email": "jean.dupont@email.com",
      "phone_number": "+243898900119",
      "full_name": "Jean Dupont",
      "gender": "homme",
      "role": "user",
      "level": "intermediaire",
      "total_xp": 1250,
      "current_streak": 5,
      "total_learning_minutes": 450.0,
      "is_active": true,
      "is_verified": true,
      "gdpr_consent": true,
      "gdpr_consent_at": "2026-02-01T08:00:00",
      "last_login_at": "2026-02-09T10:30:00",
      "created_at": "2026-02-01T08:00:00",
      "updated_at": "2026-02-09T10:30:00"
    }
  ]
}
```

---

#### `GET /api/admin/users/{user_id}`

Voir le detail d'un utilisateur.

**Auth** : Admin requis

**Reponse** `200 OK` : objet `AdminUserResponse`

---

#### `PUT /api/admin/users/{user_id}/role`

Changer le role d'un utilisateur. **Reserve au super_admin uniquement.**

**Auth** : Super Admin requis

**Body** :

| Champ  | Type   | Requis | Description                           |
|--------|--------|--------|---------------------------------------|
| `role` | string | Oui    | `user`, `admin`, `super_admin`        |

**Exemple** :
```json
{
  "role": "admin"
}
```

**Reponse** `200 OK` : objet `AdminUserResponse` mis a jour

---

#### `PUT /api/admin/users/{user_id}/activate`

Reactiver un compte utilisateur desactive.

**Auth** : Admin requis

**Reponse** `200 OK` :
```json
{
  "message": "Compte de Jean Dupont reactive avec succes."
}
```

---

#### `PUT /api/admin/users/{user_id}/deactivate`

Desactiver un compte utilisateur (l'utilisateur ne pourra plus se connecter).

**Auth** : Admin requis

**Reponse** `200 OK` :
```json
{
  "message": "Compte de Jean Dupont desactive."
}
```

---

#### `GET /api/admin/payments`

Lister tous les paiements de tous les utilisateurs.

**Auth** : Admin requis

**Query params** :

| Parametre        | Type   | Description                                      |
|------------------|--------|--------------------------------------------------|
| `status`         | string | Filtrer par statut : `completed`, `pending`, `failed` |
| `payment_method` | string | Filtrer : `carte_bancaire`, `mobile_money`       |
| `page`           | int    | Numero de page (defaut: 1)                       |
| `per_page`       | int    | Resultats par page (defaut: 50, max: 200)        |

**Reponse** `200 OK` : Liste d'objets `PaymentResponse`

---

#### `GET /api/admin/dashboard`

Dashboard administrateur avec toutes les statistiques globales en un seul appel.

**Auth** : Admin requis

**Reponse** `200 OK` :
```json
{
  "total_users": 150,
  "active_users": 142,
  "verified_users": 140,
  "new_users_today": 3,
  "new_users_this_month": 28,

  "total_subscriptions": 120,
  "active_subscriptions": 95,
  "subscriptions_by_plan": [
    {"plan": "mensuel", "count": 70, "revenue": 699.30},
    {"plan": "annuel", "count": 25, "revenue": 2249.75}
  ],

  "total_revenue": 5420.50,
  "revenue_this_month": 1250.00,
  "revenue_currency": "USD",
  "total_payments": 180,
  "completed_payments": 165,
  "failed_payments": 10,
  "pending_payments": 5,

  "total_learning_paths": 320,
  "total_sessions": 1500,
  "completed_sessions": 1200,
  "total_learning_hours": 850.5,

  "total_carbon_kg": 42.5,
  "total_trees_planted": 4,
  "total_co2_compensated_kg": 40.0
}
```

> **Frontend Admin** : Cet endpoint fournit toutes les donnees necessaires pour construire un tableau de bord d'administration complet avec KPIs, graphiques de revenus, et statistiques d'utilisation.

> **Note** : Les donnees du dashboard admin sont mises en cache Redis pendant **2 minutes** pour optimiser les performances.

---

### 5.11 Monitoring

**Prefix** : `/api/monitoring`

---

#### `GET /api/monitoring/health`

Verification de sante detaillee de tous les composants du systeme.

**Auth** : Non requise

**Reponse** `200 OK` :
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T12:00:00",
  "checks": {
    "backend": {
      "status": "up",
      "uptime_seconds": 86400,
      "uptime_human": "1j 0h 0m 0s",
      "version": "1.4.0",
      "python": "3.12.0"
    },
    "database": {
      "status": "up",
      "engine": "MySQL",
      "version": "8.0.35",
      "host": "159.89.13.54:3306"
    },
    "redis": {
      "status": "up",
      "host": "redis:6379",
      "keys": 142,
      "memory": { "used_memory_human": "15.2M" }
    },
    "ai_service": {
      "status": "up",
      "url": "http://ai-service:5000"
    },
    "backup": {
      "last_run": "2026-02-09T01:00:20",
      "last_status": "success",
      "last_tables_copied": 10,
      "last_rows_copied": 45328
    }
  }
}
```

> Les valeurs `status` globales possibles sont : `healthy`, `degraded` (un composant non critique est down).

---

#### `GET /api/monitoring/system`

Metriques systeme en temps reel (CPU, RAM, Disque, Reseau).

**Auth** : Admin (`admin` ou `super_admin`)

**Reponse** `200 OK` :
```json
{
  "timestamp": "2026-02-09T12:00:00",
  "cpu": { "percent": 35.2, "count": 4, "frequency_mhz": 2400 },
  "memory": { "total_gb": 8.0, "available_gb": 4.5, "used_gb": 3.5, "percent": 43.8 },
  "disk": { "total_gb": 100.0, "used_gb": 45.2, "free_gb": 54.8, "percent": 45.2 },
  "network": { "bytes_sent_mb": 1024.5, "bytes_recv_mb": 2048.3 },
  "process": { "pid": 1, "memory_rss_mb": 128.5, "threads": 12 },
  "platform": { "system": "Linux", "release": "5.15.0", "python": "3.12.0" }
}
```

---

#### `GET /api/monitoring/redis`

Statistiques Redis detaillees.

**Auth** : Admin

**Reponse** `200 OK` :
```json
{
  "available": true,
  "stats": { "hits": 1523, "misses": 234, "errors": 0, "sets": 892, "deletes": 45 },
  "memory": { "used_memory_human": "15.2M", "used_memory_peak_human": "18.1M" },
  "redis_stats": { "connected_clients": 12, "keyspace_hits": 5423, "keyspace_misses": 312 },
  "ecolearnai_keys": 142,
  "config": { "host": "redis", "port": 6379, "db": 0, "max_connections": 50, "default_ttl": 300 }
}
```

---

#### `GET /api/monitoring/database`

Informations detaillees sur la base de donnees MySQL.

**Auth** : Admin

**Reponse** `200 OK` :
```json
{
  "version": "8.0.35",
  "host": "159.89.13.54:3306",
  "database": "ecolearnai_db",
  "tables": [
    { "table": "users", "rows": 5000, "data_mb": 12.5, "index_mb": 3.2, "engine": "NDBCLUSTER" },
    { "table": "learning_sessions", "rows": 25000, "data_mb": 45.8, "index_mb": 8.1, "engine": "NDBCLUSTER" }
  ],
  "total_size_mb": 125.4,
  "connections": { "current": 15, "max": 500 },
  "ndb_cluster": { "Ndb_cluster_node_id": "5", "Ndb_number_of_data_nodes": "2" }
}
```

---

#### `GET /api/monitoring/backup`

Statut du systeme de backup automatique (replication cron).

**Auth** : Admin

**Reponse** `200 OK` :
```json
{
  "enabled": true,
  "schedule": "Chaque jour a 01:00 UTC",
  "backup_db": "159.89.13.55:3306/ecolearnai_db_backup",
  "current_status": {
    "last_run": "2026-02-09T01:00:20",
    "last_status": "success",
    "last_duration_seconds": 20.5,
    "last_tables_copied": 10,
    "last_rows_copied": 45328,
    "total_runs": 30,
    "total_successes": 29,
    "total_failures": 1
  },
  "history": [
    { "timestamp": "2026-02-09T01:00:20", "status": "success", "tables": 10, "rows": 45328, "duration": 20.5 },
    { "timestamp": "2026-02-08T01:00:18", "status": "success", "tables": 10, "rows": 44892, "duration": 19.8 }
  ]
}
```

---

#### `POST /api/monitoring/cache/flush`

Vider entierement le cache Redis (toutes les cles EcoLearnAI).

**Auth** : Admin

**Reponse** `200 OK` :
```json
{
  "message": "Cache Redis vide avec succes.",
  "status": "flushed"
}
```

---

## 6. Modeles de donnees (Schemas)

### UserResponse

| Champ                      | Type            | Description                                 |
|----------------------------|-----------------|---------------------------------------------|
| `id`                       | UUID            | Identifiant unique                          |
| `email`                    | string          | Adresse email                               |
| `phone_number`             | string \| null  | Numero de telephone                         |
| `full_name`                | string          | Nom complet                                 |
| `gender`                   | string \| null  | Genre                                       |
| `date_of_birth`            | string \| null  | Date de naissance (dechiffree)              |
| `nationality`              | string \| null  | Nationalite (dechiffree)                    |
| `national_id_type`         | string \| null  | Type de piece d'identite                    |
| `has_national_id`          | boolean         | Indique si un numero de piece est enregistre|
| `address_city`             | string \| null  | Ville (dechiffree)                          |
| `address_country`          | string \| null  | Pays (dechiffre)                            |
| `address_line_masked`      | string \| null  | Adresse partiellement masquee               |
| `address_postal_code_masked`| string \| null | Code postal partiellement masque            |
| `gdpr_consent`             | boolean         | Consentement traitement donnees             |
| `gdpr_consent_at`          | datetime \| null| Date du consentement                        |
| `gdpr_marketing_consent`   | boolean         | Consentement marketing                      |
| `gdpr_data_retention_consent`| boolean       | Consentement conservation donnees           |
| `avatar_url`               | string \| null  | URL de l'avatar                             |
| `bio`                      | string \| null  | Biographie                                  |
| `language`                 | string          | Langue (defaut: `fr`)                       |
| `timezone`                 | string          | Fuseau horaire (defaut: `Europe/Paris`)     |
| `level`                    | string          | Niveau d'apprentissage                      |
| `objectives`               | string \| null  | Objectifs                                   |
| `preferences`              | string \| null  | Preferences                                 |
| `total_xp`                 | int             | XP total accumule                           |
| `current_streak`           | int             | Streak actuel (jours consecutifs)           |
| `longest_streak`           | int             | Meilleur streak                             |
| `last_activity_date`       | date \| null    | Date derniere activite                      |
| `total_learning_minutes`   | float           | Temps total d'apprentissage                 |
| `role`                     | string          | Role : `user`, `admin`, `super_admin`       |
| `is_active`                | boolean         | Compte actif                                |
| `is_verified`              | boolean         | Compte verifie par SMS                      |
| `last_login_at`            | datetime \| null| Derniere connexion                          |
| `created_at`               | datetime        | Date de creation                            |
| `updated_at`               | datetime \| null| Date de mise a jour                         |

### SubscriptionResponse

| Champ        | Type     | Description                     |
|--------------|----------|---------------------------------|
| `id`         | UUID     | Identifiant unique              |
| `user_id`    | UUID     | ID de l'utilisateur             |
| `plan`       | string   | `mensuel` ou `annuel`           |
| `price`      | float    | Prix en USD                     |
| `currency`   | string   | Devise (USD)                    |
| `is_active`  | boolean  | Abonnement actif                |
| `start_date` | datetime | Date de debut                   |
| `end_date`   | datetime | Date de fin                     |
| `auto_renew` | boolean  | Renouvellement automatique      |
| `created_at` | datetime | Date de creation                |

### PaymentResponse

| Champ                    | Type            | Description                      |
|--------------------------|-----------------|----------------------------------|
| `id`                     | UUID            | Identifiant unique               |
| `user_id`                | UUID            | ID de l'utilisateur              |
| `subscription_id`        | UUID            | ID de l'abonnement               |
| `amount`                 | float           | Montant                          |
| `currency`               | string          | Devise                           |
| `payment_method`         | string          | `carte_bancaire` / `mobile_money`|
| `status`                 | string          | `pending` / `completed` / `failed`|
| `transaction_ref`        | string          | Reference de transaction         |
| `invoice_number`         | string          | Numero de facture                |
| `invoice_details`        | string \| null  | Detail de la facture             |
| `moko_transaction_uuid`  | string \| null  | UUID Moko (carte uniquement)     |
| `moko_payment_url`       | string \| null  | URL de paiement Moko             |
| `paid_at`                | datetime \| null| Date de paiement                 |
| `created_at`             | datetime        | Date de creation                 |

### LearningPathResponse

| Champ                | Type            | Description                   |
|----------------------|-----------------|-------------------------------|
| `id`                 | UUID            | Identifiant unique            |
| `user_id`            | UUID            | ID de l'utilisateur           |
| `title`              | string          | Titre du parcours             |
| `description`        | string \| null  | Description                   |
| `subject`            | string          | Sujet                         |
| `difficulty`         | string          | Niveau de difficulte          |
| `total_sessions`     | int             | Nombre total de sessions      |
| `completed_sessions` | int             | Sessions terminees            |
| `progress_percent`   | float           | Pourcentage de progression    |
| `status`             | string          | `en_cours` / `termine`        |
| `created_at`         | datetime        | Date de creation              |
| `updated_at`         | datetime        | Date de mise a jour           |

### ChatMessageResponse

| Champ             | Type     | Description                           |
|-------------------|----------|---------------------------------------|
| `id`              | UUID     | Identifiant unique                    |
| `conversation_id` | string   | ID de la conversation                 |
| `role`            | string   | `"user"` ou `"assistant"`             |
| `content`         | string   | Contenu du message                    |
| `tokens_used`     | int      | Tokens OpenAI consommes               |
| `created_at`      | datetime | Date de creation                      |

### SessionResponse

| Champ              | Type            | Description                      |
|--------------------|-----------------|----------------------------------|
| `id`               | UUID            | Identifiant unique               |
| `user_id`          | UUID            | ID de l'utilisateur              |
| `learning_path_id` | UUID            | ID du parcours parent            |
| `title`            | string          | Titre de la session              |
| `content`          | string \| null  | Contenu genere par IA            |
| `duration_minutes` | float           | Duree en minutes                 |
| `score`            | float \| null   | Score (0-100)                    |
| `session_number`   | int             | Numero de la session             |
| `status`           | string          | `en_cours` / `terminee`          |
| `started_at`       | datetime        | Date de debut                    |
| `completed_at`     | datetime \| null| Date de fin                      |
| `created_at`       | datetime        | Date de creation                 |

### CarbonSummary

| Champ                      | Type  | Description                              |
|----------------------------|-------|------------------------------------------|
| `total_sessions`           | int   | Nombre total de sessions comptabilisees  |
| `total_duration_minutes`   | float | Duree totale en minutes                  |
| `total_energy_kwh`         | float | Energie consommee en kWh                 |
| `total_carbon_kg`          | float | CO2 emis en kg                           |
| `total_trees_planted`      | int   | Arbres plantes en compensation           |
| `total_co2_compensated_kg` | float | CO2 compense en kg                       |
| `compensation_threshold_kg`| float | Seuil de declenchement (kg)              |
| `next_compensation_in_kg`  | float | Reste avant prochaine compensation       |

### DashboardData

| Champ                       | Type               | Description                   |
|-----------------------------|---------------------|-------------------------------|
| `total_learning_paths`      | int                | Parcours total                |
| `active_learning_paths`     | int                | Parcours en cours             |
| `completed_learning_paths`  | int                | Parcours termines             |
| `total_sessions`            | int                | Sessions totales              |
| `completed_sessions`        | int                | Sessions terminees            |
| `average_score`             | float \| null      | Score moyen                   |
| `total_learning_hours`      | float              | Heures d'apprentissage        |
| `total_xp`                  | int                | XP total                     |
| `level`                     | string             | Niveau actuel                 |
| `current_streak`            | int                | Streak actuel                 |
| `longest_streak`            | int                | Meilleur streak               |
| `achievements_unlocked`     | int                | Badges debloques              |
| `carbon_summary`            | CarbonSummary      | Resume carbone                |
| `compensations`             | CompensationResponse[] | Dernieres compensations   |

### PlanResponse (Admin)

| Champ                  | Type            | Description                           |
|------------------------|-----------------|---------------------------------------|
| `id`                   | UUID            | Identifiant unique                    |
| `code`                 | string          | Code unique du plan                   |
| `name`                 | string          | Nom affiche                           |
| `description`          | string \| null  | Description                           |
| `price`                | float           | Prix                                  |
| `currency`             | string          | Devise                                |
| `duration_days`        | int             | Duree en jours                        |
| `is_active`            | boolean         | Disponible a la vente                 |
| `features`             | string \| null  | Fonctionnalites (JSON)                |
| `max_sessions_per_day` | int \| null     | Limite sessions/jour                  |
| `sort_order`           | int             | Ordre d'affichage                     |
| `created_at`           | datetime        | Date de creation                      |
| `updated_at`           | datetime        | Date de mise a jour                   |

### AdminUserResponse

| Champ                    | Type            | Description                           |
|--------------------------|-----------------|---------------------------------------|
| `id`                     | UUID            | Identifiant unique                    |
| `email`                  | string          | Adresse email                         |
| `phone_number`           | string \| null  | Numero de telephone                   |
| `full_name`              | string          | Nom complet                           |
| `gender`                 | string \| null  | Genre                                 |
| `role`                   | string          | Role (`user`, `admin`, `super_admin`) |
| `level`                  | string          | Niveau d'apprentissage                |
| `total_xp`               | int             | XP total                              |
| `current_streak`         | int             | Streak actuel                         |
| `total_learning_minutes` | float           | Temps d'apprentissage                 |
| `is_active`              | boolean         | Compte actif                          |
| `is_verified`            | boolean         | Verifie par SMS                       |
| `gdpr_consent`           | boolean         | Consentement RGPD                     |
| `gdpr_consent_at`        | datetime \| null| Date du consentement                  |
| `last_login_at`          | datetime \| null| Derniere connexion                    |
| `created_at`             | datetime        | Date de creation                      |
| `updated_at`             | datetime \| null| Date de mise a jour                   |

### AdminStats (Dashboard)

| Champ                    | Type            | Description                           |
|--------------------------|-----------------|---------------------------------------|
| `total_users`            | int             | Nombre total d'utilisateurs           |
| `active_users`           | int             | Utilisateurs actifs                   |
| `verified_users`         | int             | Utilisateurs verifies                 |
| `new_users_today`        | int             | Nouveaux aujourd'hui                  |
| `new_users_this_month`   | int             | Nouveaux ce mois                      |
| `total_subscriptions`    | int             | Abonnements totaux                    |
| `active_subscriptions`   | int             | Abonnements actifs                    |
| `subscriptions_by_plan`  | list[dict]      | Repartition par plan                  |
| `total_revenue`          | float           | Revenu total                          |
| `revenue_this_month`     | float           | Revenu ce mois                        |
| `revenue_currency`       | string          | Devise des revenus                    |
| `total_payments`         | int             | Paiements totaux                      |
| `completed_payments`     | int             | Paiements reussis                     |
| `failed_payments`        | int             | Paiements echoues                     |
| `pending_payments`       | int             | Paiements en attente                  |
| `total_learning_paths`   | int             | Parcours crees                        |
| `total_sessions`         | int             | Sessions totales                      |
| `completed_sessions`     | int             | Sessions terminees                    |
| `total_learning_hours`   | float           | Heures d'apprentissage globales       |
| `total_carbon_kg`        | float           | CO2 total emis (kg)                   |
| `total_trees_planted`    | int             | Arbres plantes                        |
| `total_co2_compensated_kg`| float          | CO2 compense (kg)                     |

---

## 7. Codes d'erreur

| Code HTTP | Signification                              | Quand                                          |
|-----------|--------------------------------------------|-------------------------------------------------|
| `200`     | Succes                                     | Requete traitee avec succes                     |
| `201`     | Cree                                       | Ressource creee (inscription, parcours, session)|
| `400`     | Requete invalide                           | Donnees manquantes ou invalides                 |
| `401`     | Non authentifie                            | Token manquant, expire ou invalide              |
| `403`     | Interdit                                   | Compte non verifie, desactive, role insuffisant, ou **abonnement requis** (POST /api/learning/paths, POST /api/learning/sessions) |
| `404`     | Non trouve                                 | Ressource inexistante                           |
| `422`     | Erreur de validation                       | Champs invalides (Pydantic)                     |
| `502`     | Erreur passerelle                          | Echec appel API externe (Moko, SMS)             |

### Format des erreurs

```json
{
  "detail": "Message d'erreur explicite en francais."
}
```

### Format des erreurs de validation (422)

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Le mot de passe doit contenir au moins 8 caracteres.",
      "type": "value_error"
    },
    {
      "loc": ["body", "gdpr_consent"],
      "msg": "Le consentement au traitement des donnees personnelles est obligatoire...",
      "type": "value_error"
    }
  ]
}
```

> **Frontend** : Parcourir le tableau `detail` pour afficher les erreurs champ par champ dans le formulaire.

---

## 8. Securite & RGPD

### Donnees chiffrees en base (Fernet AES-128-CBC)

Les champs suivants sont **chiffres avant stockage** et **dechiffres a la lecture** :

| Champ en base                    | Donnee               |
|----------------------------------|-----------------------|
| `encrypted_date_of_birth`        | Date de naissance     |
| `encrypted_nationality`          | Nationalite           |
| `encrypted_national_id`          | Numero piece identite |
| `encrypted_address_line`         | Adresse (rue)         |
| `encrypted_address_city`         | Ville                 |
| `encrypted_address_postal_code`  | Code postal           |
| `encrypted_address_country`      | Pays                  |

### Mot de passe

- Hache avec **bcrypt** (irreversible)
- Jamais stocke en clair, jamais retourne dans les reponses API

### Regle du mot de passe

| Regle                    | Detail                    |
|--------------------------|---------------------------|
| Longueur minimum         | 8 caracteres              |
| Majuscule                | Au moins 1 lettre [A-Z]   |
| Minuscule                | Au moins 1 lettre [a-z]   |
| Chiffre                  | Au moins 1 chiffre [0-9]  |
| Caractere special        | Au moins 1 parmi `!@#$%^&*()_+-=[]{}|;:'",.<>?/\`` |

### Principe de minimisation RGPD

- `GET /api/users/me` : l'adresse est **partiellement masquee** (ex: `12 Ru***`, `75***`)
- Le numero de piece d'identite n'est **jamais** retourne (seul `has_national_id: true/false`)
- Pour un export complet : `GET /api/users/me/data-export`

### Controle d'acces par roles (RBAC)

Le systeme utilise trois niveaux de roles :

| Role           | Description                                          | Acces                                   |
|----------------|------------------------------------------------------|-----------------------------------------|
| `user`         | Utilisateur standard (par defaut a l'inscription)    | Endpoints `/api/auth`, `/api/users`, `/api/learning`, `/api/carbon`, `/api/dashboard`, `/api/subscriptions`, `/api/payments` |
| `admin`        | Administrateur                                       | Tout ce que `user` peut faire + tous les endpoints `/api/admin/*` |
| `super_admin`  | Super administrateur                                 | Tout ce que `admin` peut faire + gestion des roles (`PUT /api/admin/users/{id}/role`) |

**Regles importantes :**
- Un `admin` ne peut **pas** changer les roles d'autres utilisateurs (seul `super_admin` le peut)
- Un `admin` ne peut **pas** desactiver un `super_admin`
- Le `super_admin` initial est cree via `POST /api/admin/seed-admin` (une seule fois)
- Les tokens JWT contiennent le `sub` (user ID) mais **pas** le role ; le role est verifie en base a chaque requete admin

### Droits RGPD implementes

| Droit                | Article | Endpoint                          |
|----------------------|---------|-----------------------------------|
| Droit d'acces        | Art. 15 | `GET /api/users/me`               |
| Droit de rectification| Art. 16| `PUT /api/users/me`               |
| Droit a l'effacement | Art. 17 | `DELETE /api/users/me`            |
| Droit a la portabilite| Art. 20| `GET /api/users/me/data-export`   |
| Gestion du consentement| Art. 7| `PUT /api/users/me/gdpr-consent`  |
| Droit a l'information| Art. 13-14| `GET /api/users/me/privacy-info`|

---

## 9. Exemples d'integration Frontend

### Configuration Axios / Fetch

```javascript
// === Configuration de base ===
const API_BASE_URL = 'http://localhost:8000';

// === Helper pour les requetes authentifiees ===
function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
}

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: getAuthHeaders(),
    ...options,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erreur serveur');
  }

  return response.json();
}
```

### Inscription complete

```javascript
async function register(userData) {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: userData.email,
      password: userData.password,
      full_name: userData.fullName,
      phone_number: userData.phoneNumber,   // Format: "+243898900119"
      date_of_birth: userData.dateOfBirth,  // Format: "1990-05-15"
      gender: userData.gender,              // "homme" | "femme" | "autre" | "non_precise"
      nationality: userData.nationality,
      address_city: userData.city,
      address_country: userData.country,
      gdpr_consent: true,                   // OBLIGATOIRE
      gdpr_marketing_consent: userData.marketingConsent || false,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    // Gestion des erreurs de validation (422)
    if (response.status === 422) {
      const errors = data.detail.map(e => ({
        field: e.loc[e.loc.length - 1],
        message: e.msg,
      }));
      throw { type: 'validation', errors };
    }
    throw new Error(data.detail);
  }

  // Le code OTP est envoye par SMS et par email
  // Rediriger vers la page de verification
  // data.sms_sent, data.email_sent => verifier les envois
  return data; // data.verification_required === true
}
```

### Verification OTP (SMS ou Email)

```javascript
async function verifyOTP(email, code) {
  // Le meme code est envoye par SMS et par email
  // L'utilisateur peut saisir le code recu sur l'un ou l'autre canal
  const response = await fetch(`${API_BASE_URL}/api/auth/verify-sms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail);
  }

  // Compte verifie ! Rediriger vers login
  return data;
}

// Renvoyer le code OTP (par SMS et email)
async function resendOTP(email) {
  const response = await fetch(`${API_BASE_URL}/api/auth/resend-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });

  const data = await response.json();
  // data.sms_sent, data.email_sent => verifier les envois
  return data;
}
```

### Connexion

```javascript
async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);       // ATTENTION: le champ s'appelle "username"
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    if (response.status === 403) {
      // Compte non verifie => rediriger vers verification SMS
      throw { type: 'not_verified', message: data.detail };
    }
    throw new Error(data.detail);
  }

  // Stocker le token
  localStorage.setItem('access_token', data.access_token);
  return data.user;
}
```

### Flux de paiement carte bancaire

```javascript
async function subscribeWithCard(plan) {
  // 1. Initier l'abonnement
  const data = await apiRequest('/api/subscriptions/subscribe', {
    method: 'POST',
    body: JSON.stringify({
      plan: plan,               // "mensuel" ou "annuel"
      payment_method: 'carte_bancaire',
    }),
  });

  // 2. Rediriger vers la page de paiement Moko
  window.location.href = data.payment_url;

  // Note: apres le paiement, l'utilisateur est redirige vers votre site
  // Utiliser le polling ci-dessous pour verifier le statut
}

// 3. Polling du statut de paiement (page de retour)
async function pollPaymentStatus(paymentId, maxAttempts = 20) {
  for (let i = 0; i < maxAttempts; i++) {
    const data = await apiRequest(`/api/payments/${paymentId}/status`);

    if (data.status === 'completed') {
      // Paiement reussi !
      return { success: true, data };
    }

    if (data.status === 'failed') {
      // Paiement echoue
      return { success: false, data };
    }

    // Attendre 3 secondes avant le prochain appel
    await new Promise(resolve => setTimeout(resolve, 3000));
  }

  return { success: false, timeout: true };
}
```

### Charger le dashboard

```javascript
async function loadDashboard() {
  const data = await apiRequest('/api/dashboard/');

  // data contient toutes les stats en un seul appel :
  // - data.total_xp, data.level, data.current_streak
  // - data.total_learning_paths, data.completed_learning_paths
  // - data.carbon_summary.total_carbon_kg
  // - data.compensations (liste des compensations ecologiques)

  return data;
}
```

### Export RGPD

```javascript
async function downloadMyData() {
  const data = await apiRequest('/api/users/me/data-export');

  // Generer un fichier JSON telecharable
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ecolearnai-export-${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
```

### Administration : Initialiser le premier admin

```javascript
// A appeler une seule fois au deploiement initial
async function seedAdmin() {
  const response = await fetch(`${API_BASE_URL}/api/admin/seed-admin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  const data = await response.json();
  // { email: "admin@ecolearnai.com", password: "Admin@2026!", role: "super_admin" }
  console.log('Admin cree :', data.email);
  console.log('Mot de passe temporaire :', data.password);
  // IMPORTANT : changer le mot de passe immediatement !
}
```

### Administration : Gestion des plans d'abonnement

```javascript
// Creer un plan mensuel
async function createPlan() {
  return await apiRequest('/api/admin/plans', {
    method: 'POST',
    body: JSON.stringify({
      code: 'mensuel',
      name: 'Abonnement Mensuel',
      description: 'Acces complet pendant 30 jours',
      price: 9.99,
      currency: 'USD',
      duration_days: 30,
      is_active: true,
      sort_order: 1,
    }),
  });
}

// Modifier le prix d'un plan
async function updatePlanPrice(planId, newPrice) {
  return await apiRequest(`/api/admin/plans/${planId}`, {
    method: 'PUT',
    body: JSON.stringify({ price: newPrice }),
  });
}

// Lister tous les plans (y compris inactifs)
async function listAllPlans() {
  return await apiRequest('/api/admin/plans?include_inactive=true');
}

// Supprimer/desactiver un plan
async function deletePlan(planId) {
  return await apiRequest(`/api/admin/plans/${planId}`, {
    method: 'DELETE',
  });
}
```

### Administration : Gestion des utilisateurs

```javascript
// Lister les utilisateurs avec pagination et recherche
async function listUsers(page = 1, search = '', role = '') {
  let url = `/api/admin/users?page=${page}&per_page=20`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (role) url += `&role=${role}`;
  return await apiRequest(url);
}

// Changer le role d'un utilisateur (super_admin uniquement)
async function changeUserRole(userId, newRole) {
  return await apiRequest(`/api/admin/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role: newRole }),  // 'user', 'admin', 'super_admin'
  });
}

// Desactiver un compte
async function deactivateUser(userId) {
  return await apiRequest(`/api/admin/users/${userId}/deactivate`, {
    method: 'PUT',
  });
}

// Reactiver un compte
async function activateUser(userId) {
  return await apiRequest(`/api/admin/users/${userId}/activate`, {
    method: 'PUT',
  });
}
```

### Administration : Dashboard

```javascript
async function loadAdminDashboard() {
  const stats = await apiRequest('/api/admin/dashboard');

  // stats contient :
  // --- Utilisateurs ---
  // stats.total_users, stats.active_users, stats.verified_users
  // stats.new_users_today, stats.new_users_this_month

  // --- Abonnements ---
  // stats.total_subscriptions, stats.active_subscriptions
  // stats.subscriptions_by_plan (repartition par type de plan)

  // --- Revenus ---
  // stats.total_revenue, stats.revenue_this_month, stats.revenue_currency
  // stats.total_payments, stats.completed_payments, stats.failed_payments

  // --- Apprentissage ---
  // stats.total_learning_paths, stats.total_sessions, stats.completed_sessions
  // stats.total_learning_hours

  // --- Ecologie ---
  // stats.total_carbon_kg, stats.total_trees_planted, stats.total_co2_compensated_kg

  return stats;
}
```

---

## Notes pour l'equipe Frontend

1. **Swagger interactif** : Testez tous les endpoints directement sur `http://localhost:8000/docs`
2. **CORS** : Le backend accepte toutes les origines (`*`). Pas de configuration CORS necessaire en dev.
3. **Dates** : Toutes les dates sont au format ISO 8601 (`2026-02-09T10:30:00`)
4. **UUID** : Tous les identifiants sont des UUID v4
5. **Pagination** : Implementee sur les endpoints admin (`page`, `per_page`). Les endpoints utilisateur retournent tous les elements.
6. **Temps reel** : Pas de WebSocket. Utiliser le polling pour le statut de paiement.
7. **Erreurs** : Toujours verifier `response.ok` avant de lire le body. Les erreurs sont en francais.
8. **Login** : Le endpoint `/api/auth/login` utilise `application/x-www-form-urlencoded`, pas JSON !
9. **Content-Type** : Tous les autres endpoints POST/PUT utilisent `application/json`.
10. **Token** : Le token JWT expire apres 30 minutes. Implementer un mecanisme de refresh ou de re-login.
11. **Roles** : Verifier le `role` de l'utilisateur dans la reponse de login pour afficher les interfaces admin.
12. **Plans dynamiques** : Les plans d'abonnement sont configures par les admins. Utiliser `GET /api/subscriptions/plans` pour afficher les plans disponibles.
13. **Verification double canal** : Le code OTP est envoye par SMS **et** par email. L'utilisateur peut utiliser le code recu sur l'un ou l'autre canal.
14. **Notifications paiement** : Les confirmations/echecs de paiement sont envoyes automatiquement par SMS et email.
15. **Cache Redis** : Les dashboards (admin et utilisateur) sont caches pendant 2-3 minutes. Apres une action (ex: terminer une session), les nouvelles valeurs apparaissent apres expiration du cache.
16. **Monitoring** : `GET /api/monitoring/health` est public et peut etre utilise pour un indicateur de sante dans le frontend. Les autres endpoints monitoring sont reserves aux admins.
17. **Grafana** : Un dashboard visuel est disponible sur `http://localhost:3000` (admin / EcoLearn@Grafana2026) pour le monitoring temps reel.
18. **Backup** : La base de donnees est automatiquement repliquee chaque jour a 01:00 UTC vers un serveur de backup. Statut consultable via `GET /api/monitoring/backup`.
19. **Abonnement** : Les endpoints de creation de parcours et sessions renvoient `403` si l'utilisateur n'a pas d'abonnement actif. Verifier `GET /api/subscriptions/my` et afficher un CTA d'abonnement si aucun abonnement actif.
20. **Chatbot** : Le chatbot (`/api/chatbot/send`) est accessible a TOUS les utilisateurs authentifies, meme sans abonnement. Pour les non-abonnes, le chatbot suggere naturellement de souscrire.

---


