# EcoLearn AI

**Version** : 1.4.0

**Plateforme d'apprentissage en ligne intelligente et écologique.**

EcoLearn AI améliore l'efficacité de la formation numérique tout en réduisant et compensant son impact environnemental. La plateforme s'appuie sur l'intelligence artificielle (OpenAI GPT) pour générer des parcours d'apprentissage personnalisés.

---

## Architecture

| Composant | Technologie | Port |
|-----------|-------------|------|
| Backend API | FastAPI (Python) | 8000 |
| Service IA | Flask + OpenAI GPT | 5000 |
| Base de données | MySQL 8.0 NDB Cluster | 3306 (remote) |
| Cache | Redis 7.2 | 6379 |
| Monitoring | Prometheus | 9090 |
| Dashboards | Grafana | 3000 |
| Orchestration | Docker Compose | — |

## Fonctionnalites

- **Parcours personnalises** : IA generative (GPT) adaptant le contenu au niveau, objectifs et preferences de l'utilisateur
- **Chatbot IA** : Assistant conversationnel intelligent accessible a tous les utilisateurs (avec ou sans abonnement)
- **Restriction abonnement** : Generation de cours reserves aux abonnes, chatbot gratuit pour tous
- **Comptes securises** : Authentification JWT, suivi pedagogique et environnemental
- **Abonnements** : Modele mensuel/annuel avec paiement par carte bancaire ou mobile money
- **Facturation automatique** : Chaque paiement genere une facture consultable
- **Sessions d'apprentissage** : Suivi de duree, progression et performance
- **Empreinte carbone** : Calcul automatique par session (duree, energie, region serveur)
- **Compensation ecologique** : Plantation d'arbres via partenaires quand les seuils sont atteints
- **Cache Redis** : Performances optimisees avec mise en cache intelligente
- **Monitoring** : Prometheus + Grafana pour le suivi temps reel
- **Backup automatique** : Replication quotidienne de la base de donnees
- **Dashboard interactif** : Visualisation progression, impact carbone, actions ecologiques

## Demarrage rapide

### Prerequis
- Docker et Docker Compose
- Cle API OpenAI (pour le service IA)

### Installation

```bash
# 1. Cloner le projet
git clone <repo-url>
cd ProEcoIt

# 2. Configurer l'environnement
cp .env.example .env
# Editer .env avec votre cle OpenAI et vos parametres

# 3. Lancer tous les services
docker-compose up --build

# 4. Acceder a l'application
# API Backend : http://localhost:8000/docs
# Service IA : http://localhost:5000
# Grafana : http://localhost:3000
```

## Structure du projet

```
ProEcoIt/
├── docker-compose.yml
├── .env.example
├── API_DOCUMENTATION.md
├── CURL_COMMANDS.md
├── ARCHITECTURE.md
├── DATABASE_ARCHITECTURE.md
├── UML_CAMUNDA.md
├── backend/
│   ├── app/
│   │   ├── models/       # Modeles SQLAlchemy (11 tables)
│   │   ├── schemas/      # Schemas Pydantic
│   │   ├── routers/      # Routes API (auth, users, learning, chatbot, admin, etc.)
│   │   ├── services/     # Logique metier (cache, backup, carbon, email, sms, etc.)
│   │   └── utils/        # Securite (JWT, chiffrement, roles)
│   ├── Dockerfile
│   └── requirements.txt
├── ai-service/
│   ├── app.py            # Flask API (generate + chat)
│   ├── services/
│   ├── Dockerfile
│   └── requirements.txt
├── monitoring/
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   └── grafana/
└── generate_pptx.py      # Generateur de presentation
```

## Licence

Projet prive - EcoLearn AI.
