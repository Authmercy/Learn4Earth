# EcoLearn AI - Architecture Systeme

**Version** : 1.3.0
**Date** : 09/02/2026

---

## 1. Vue d'ensemble

```
                                    ARCHITECTURE ECOLEARNAI
                                    ======================

    +------------------+
    |   UTILISATEUR    |
    |  (Navigateur /   |
    |   Mobile App)    |
    +--------+---------+
             |
             | HTTPS (443)
             |
    +--------v---------+
    |    CLOUDFLARE     |    CDN + Protection DDoS + Cache statique
    |   (CDN / WAF)    |    SSL/TLS termination
    +--------+---------+
             |
             | HTTPS
             |
    +--------v---------+
    |     NGINX         |    Load Balancer / Reverse Proxy
    |  Load Balancer    |    Rate Limiting, Compression gzip
    |  (Port 80/443)    |    Routing : /api/* -> Backend, /* -> Frontend
    +---+----------+----+
        |          |
        |          |
   +----v----+ +---v--------+
   |FRONTEND | | FRONTEND   |     2+ instances React/Next.js
   | App #1  | | App #2     |     Rendu SSR ou SPA statique
   | (3000)  | | (3001)     |     Cache navigateur
   +---------+ +------------+
        |          |
        | HTTP (interne)
        |
   +----v---------------------------------+
   |         NGINX API Gateway            |    Reverse proxy API
   |         (Port 8080 interne)          |    Rate limiting par IP/token
   |                                      |    CORS, Headers securite
   +---+----------+----------+-----------+
       |          |          |
       |          |          |
  +----v----+ +--v------+ +-v----------+
  |BACKEND  | |BACKEND  | |BACKEND     |    2-3 instances FastAPI
  | API #1  | |API #2   | |API #3      |    Uvicorn workers
  | (8000)  | |(8001)   | |(8002)      |    Stateless (JWT)
  +----+----+ +---+-----+ +-----+------+
       |          |              |
       +----------+--------------+
                  |
       +----------+--------------+--------------+
       |          |              |              |
  +----v----+ +--v------+ +----v-----+ +------v------+
  | MySQL   | | Redis   | | AI Svc   | | File Store  |
  | (3306)  | | (6379)  | | (5000)   | | (S3/Minio)  |
  |Distant  | | Cache & | | Flask +  | | Avatars,    |
  |159.89.. | | Sessions| | OpenAI   | | Exports     |
  +---------+ +---------+ +----------+ +-------------+
                  |
       +----------+--------------+--------------+
       |          |              |              |
  +----v----+ +--v------+ +----v-----+ +------v------+
  | Umoja   | | MGT-SMS | | Gmail    | | OpenAI      |
  | CardAPI | | API     | | SMTP     | | GPT API     |
  | (Visa/  | | (OTP &  | | (Email   | | (Contenu    |
  | MC)     | | Notif)  | | confirm) | | pedagogique)|
  +---------+ +---------+ +----------+ +-------------+
     SERVICES TIERS EXTERNES
```

---

## 2. Detail des couches

### 2.1 Couche Client (Utilisateur)

```
+------------------------------------------------------------------+
|                        UTILISATEUR                                |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  | Navigateur Web   |  | Application      |  | Application      | |
|  | (Chrome, Safari  |  | Mobile iOS       |  | Mobile Android   | |
|  |  Firefox)        |  | (React Native)   |  | (React Native)   | |
|  +--------+---------+  +--------+---------+  +--------+---------+ |
|           |                      |                     |          |
+-----------+----------------------+---------------------+----------+
            |                      |                     |
            +----------------------+---------------------+
                                   |
                            HTTPS / WSS
                                   |
                                   v
                          [CLOUDFLARE CDN]
```

**Responsabilites** :
- Interface utilisateur (React.js / Next.js)
- Stockage local du JWT token (`localStorage` ou `httpOnly cookie`)
- Gestion du cache navigateur
- Appels API REST vers le backend
- Gestion offline (Service Worker optionnel)

---

### 2.2 Couche CDN / Protection (Cloudflare)

```
+------------------------------------------------------------------+
|                      CLOUDFLARE                                   |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  | Protection DDoS  |  | SSL/TLS          |  | Cache Statique   | |
|  | - Rate limiting  |  | - Certificat     |  | - JS, CSS, IMG   | |
|  | - Filtrage bot   |  | - HTTPS force    |  | - TTL configure  | |
|  | - Geoblocage     |  | - TLS 1.3        |  | - Purge API      | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+                       |
|  | WAF (Firewall)   |  | DNS Management   |                      |
|  | - Regles OWASP   |  | - ecolearnai.com |                      |
|  | - SQL injection   |  | - api.ecolearnai |                      |
|  | - XSS protection |  | - admin.ecolearn |                      |
|  +------------------+  +------------------+                       |
+------------------------------------------------------------------+
```

---

### 2.3 Couche Load Balancer (Nginx)

```
+------------------------------------------------------------------+
|                    NGINX LOAD BALANCER                             |
|                    (Serveur principal)                             |
+------------------------------------------------------------------+
|                                                                   |
|  Routing :                                                        |
|  ┌─────────────────────────────────────────────────────────┐      |
|  │  ecolearnai.com/*           -> Frontend (upstream_web)  │      |
|  │  ecolearnai.com/api/*       -> Backend  (upstream_api)  │      |
|  │  ecolearnai.com/docs        -> Backend  (Swagger)       │      |
|  │  ecolearnai.com/admin/*     -> Frontend (panel admin)   │      |
|  │  api.ecolearnai.com/*       -> Backend  (upstream_api)  │      |
|  └─────────────────────────────────────────────────────────┘      |
|                                                                   |
|  Load Balancing (Round Robin / Least Connections) :               |
|  ┌─────────────────────┐  ┌─────────────────────┐                |
|  │  upstream_web:       │  │  upstream_api:       │                |
|  │    frontend:3000     │  │    backend:8000      │                |
|  │    frontend:3001     │  │    backend:8001      │                |
|  │                      │  │    backend:8002      │                |
|  └─────────────────────┘  └─────────────────────┘                |
|                                                                   |
|  Securite :                                                       |
|  - Rate limiting : 100 req/min par IP                             |
|  - Compression gzip/brotli                                        |
|  - Headers securite (HSTS, X-Frame, CSP)                          |
|  - Timeout : 30s pour API, 10s pour statique                      |
+------------------------------------------------------------------+
```

**Configuration Nginx type** :

```nginx
# /etc/nginx/conf.d/ecolearnai.conf

upstream frontend_servers {
    least_conn;
    server frontend-1:3000;
    server frontend-2:3001;
}

upstream backend_servers {
    least_conn;
    server backend-1:8000;
    server backend-2:8001;
    server backend-3:8002;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

server {
    listen 443 ssl http2;
    server_name ecolearnai.com;

    ssl_certificate     /etc/ssl/ecolearnai.com.pem;
    ssl_certificate_key /etc/ssl/ecolearnai.com.key;

    # Headers securite
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Frontend
    location / {
        proxy_pass http://frontend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API Backend
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    # Auth (rate limiting strict)
    location /api/auth/ {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Swagger / ReDoc
    location /docs {
        proxy_pass http://backend_servers;
    }
    location /redoc {
        proxy_pass http://backend_servers;
    }

    # Callback paiement (pas de rate limit)
    location /api/payments/moko/callback {
        proxy_pass http://backend_servers;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### 2.4 Couche Backend (FastAPI - Microservices)

```
+------------------------------------------------------------------+
|                    BACKEND FASTAPI                                 |
|              (2-3 instances, stateless)                           |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------------------------------------------------+ |
|  |                    FastAPI Application                        | |
|  +-------------------------------------------------------------+ |
|  |                                                               | |
|  |  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       | |
|  |  │  Middleware   │  │  Middleware   │  │  Middleware   │       | |
|  |  │  CORS        │  │  Auth JWT    │  │  Rate Limit  │       | |
|  |  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       | |
|  |         └─────────────────┼─────────────────┘               | |
|  |                           │                                   | |
|  |  ┌────────────────────────v────────────────────────────┐     | |
|  |  │                    ROUTERS                           │     | |
|  |  ├─────────────┬──────────────┬──────────────┐         │     | |
|  |  │ /api/auth   │ /api/users   │ /api/admin   │         │     | |
|  |  │ - register  │ - profile    │ - plans CRUD │         │     | |
|  |  │ - login     │ - password   │ - users mgmt │         │     | |
|  |  │ - verify    │ - RGPD       │ - dashboard  │         │     | |
|  |  │ - resend    │ - progression│ - payments   │         │     | |
|  |  ├─────────────┼──────────────┼──────────────┤         │     | |
|  |  │/api/subscr. │/api/learning │/api/carbon   │         │     | |
|  |  │ - plans     │ - paths      │ - summary    │         │     | |
|  |  │ - subscribe │ - sessions   │ - footprints │         │     | |
|  |  │ - my subs   │ - complete   │ - compensate │         │     | |
|  |  ├─────────────┼──────────────┼──────────────┤         │     | |
|  |  │/api/payments│/api/dashboard│              │         │     | |
|  |  │ - my        │ - stats      │              │         │     | |
|  |  │ - invoice   │ - carbon     │              │         │     | |
|  |  │ - status    │ - gamif.     │              │         │     | |
|  |  │ - callback  │              │              │         │     | |
|  |  └─────────────┴──────────────┴──────────────┘         │     | |
|  |                           │                                   | |
|  |  ┌────────────────────────v────────────────────────────┐     | |
|  |  │                   SERVICES                           │     | |
|  |  ├───────────────┬────────────────┬────────────────────┤     | |
|  |  │ PaymentService│ ProgressionSvc │ CarbonService      │     | |
|  |  │ MokoService   │ SMSService     │ EmailService       │     | |
|  |  │ EncryptionSvc │                │                    │     | |
|  |  └───────────────┴────────────────┴────────────────────┘     | |
|  |                           │                                   | |
|  |  ┌────────────────────────v────────────────────────────┐     | |
|  |  │                    MODELS (ORM)                      │     | |
|  |  │  User | Subscription | Payment | LearningPath       │     | |
|  |  │  LearningSession | CarbonFootprint | EcoCompensation│     | |
|  |  │  Achievement | UserAchievement | SubscriptionPlan    │     | |
|  |  └────────────────────────┬────────────────────────────┘     | |
|  |                           │                                   | |
|  +---------------------------│-----------------------------------+ |
|                              │                                    |
+------------------------------│------------------------------------+
                               │
                    SQLAlchemy / PyMySQL
                               │
                               v
                      [MySQL 8.0 Distant]
```

---

### 2.5 Couche Donnees

```
+------------------------------------------------------------------+
|                    BASES DE DONNEES                                |
+------------------------------------------------------------------+
|                                                                   |
|  +---------------------------+  +------------------------------+  |
|  |  MySQL 8.0               |  |  Redis 7.x                   |  |
|  |  (159.89.13.54:3306)     |  |  (Cache & Sessions)          |  |
|  |                           |  |                              |  |
|  |  Tables :                 |  |  Utilisation :               |  |
|  |  - users                  |  |  - Cache plans abonnement   |  |
|  |  - subscriptions          |  |  - Sessions JWT (blacklist) |  |
|  |  - subscription_plans     |  |  - Rate limiting compteurs  |  |
|  |  - payments               |  |  - Cache dashboard stats    |  |
|  |  - learning_paths         |  |  - OTP codes temporaires    |  |
|  |  - learning_sessions      |  |  - File d'attente emails   |  |
|  |  - carbon_footprints      |  |                              |  |
|  |  - eco_compensations      |  |  TTL :                       |  |
|  |  - achievements           |  |  - Plans : 5 min             |  |
|  |  - user_achievements      |  |  - Dashboard : 1 min         |  |
|  |  - chat_messages          |  |  - OTP : 10 min              |  |
|  |  Chiffrement :            |  |                              |  |
|  |  - Fernet AES-128-CBC     |  +------------------------------+  |
|  |  - 7 champs sensibles     |                                    |
|  +---------------------------+                                    |
+------------------------------------------------------------------+
```

---

### 2.6 Services Tiers (Microservices externes)

```
+------------------------------------------------------------------+
|                  SERVICES TIERS EXTERNES                          |
+------------------------------------------------------------------+
|                                                                   |
|  +-----------------------+     +-----------------------------+    |
|  |  UMOJA / FRESHPAY     |     |  MGT-SMS API                |    |
|  |  (Paiement Carte)     |     |  (Envoi SMS)                |    |
|  +-----------------------+     +-----------------------------+    |
|  | URL: card.gofreshpay  |     | URL: api.magictech-sms.com |    |
|  |      .com             |     |                             |    |
|  | Auth: HMAC-SHA256     |     | Auth: x-api-key             |    |
|  |       (API Key +      |     |                             |    |
|  |        Secret +       |     | Flux :                       |    |
|  |        Timestamp)     |     | Backend -> MGT-SMS -> User  |    |
|  |                       |     |                             |    |
|  | Flux sortant :        |     | Utilisation :               |    |
|  | Backend -> Umoja API  |     | - OTP inscription           |    |
|  |   -> URL paiement     |     | - Notification paiement     |    |
|  |   -> Redirect user    |     | - Alertes compte            |    |
|  |                       |     +-----------------------------+    |
|  | Flux entrant :        |                                        |
|  | Umoja -> Callback     |     +-----------------------------+    |
|  |   -> /api/payments/   |     |  GMAIL SMTP                 |    |
|  |      moko/callback    |     |  (Envoi Email)              |    |
|  |   -> HMAC verification|     +-----------------------------+    |
|  |   -> Active abonnement|     | Host: smtp.gmail.com:465    |    |
|  +-----------------------+     | Auth: App Password           |    |
|                                |                             |    |
|  +-----------------------+     | Flux :                       |    |
|  |  OPENAI GPT API       |     | Backend -> Gmail -> User    |    |
|  |  (Generation contenu) |     |                             |    |
|  +-----------------------+     | Utilisation :               |    |
|  | URL: api.openai.com   |     | - OTP (meme code que SMS)  |    |
|  | Auth: Bearer API Key  |     | - Confirmation paiement     |    |
|  | Model: GPT-4          |     | - Echec paiement            |    |
|  |                       |     +-----------------------------+    |
|  | Flux :                |                                        |
|  | Backend -> Flask AI   |                                        |
|  |   -> OpenAI API       |                                        |
|  |   -> Contenu genere   |                                        |
|  +-----------------------+                                        |
+------------------------------------------------------------------+
```

---

## 3. Flux de communication detailles

### 3.1 Flux Inscription + Verification

```
User          Frontend        Nginx LB        Backend         MySQL       SMS API     Gmail
 |               |               |               |              |            |           |
 |--Formulaire-->|               |               |              |            |           |
 |               |--POST /api/auth/register----->|              |            |           |
 |               |               |--Round Robin->|              |            |           |
 |               |               |               |--INSERT----->|            |           |
 |               |               |               |<--OK---------|            |           |
 |               |               |               |--OTP Code---------------->|           |
 |               |               |               |--OTP Code------------------------------->|
 |               |               |<-201 Created--|              |            |           |
 |               |<--Code envoye par SMS+Email---|              |            |           |
 |<--Page verif--|               |               |              |            |           |
 |               |               |               |              |            |           |
 |--Saisit code->|               |               |              |            |           |
 |               |--POST /api/auth/verify-sms--->|              |            |           |
 |               |               |--Round Robin->|              |            |           |
 |               |               |               |--UPDATE----->|            |           |
 |               |               |               |  is_verified |            |           |
 |               |               |<--200 OK------|              |            |           |
 |               |<--Compte actif!---------------|              |            |           |
 |<--Redirect -->|               |               |              |            |           |
 |   login       |               |               |              |            |           |
```

### 3.2 Flux Paiement Carte Bancaire (Umoja/Visa)

```
User          Frontend        Nginx LB        Backend         MySQL      Umoja API
 |               |               |               |              |            |
 |--Clic Payer-->|               |               |              |            |
 |               |--POST /api/subscriptions/subscribe---------->|            |
 |               |               |--Round Robin->|              |            |
 |               |               |               |--INSERT sub->|            |
 |               |               |               |  (pending)   |            |
 |               |               |               |--INSERT pay->|            |
 |               |               |               |  (pending)   |            |
 |               |               |               |              |            |
 |               |               |               |--POST /api/v1/payment/--->|
 |               |               |               |  orders (HMAC signed)     |
 |               |               |               |<-payment_url + uuid-------|
 |               |               |               |              |            |
 |               |               |               |--UPDATE pay->|            |
 |               |               |               |  moko_uuid   |            |
 |               |               |<-payment_url--|              |            |
 |               |<--Redirect to Moko------------|              |            |
 |<--Redirect--->|               |               |              |            |
 |               |               |               |              |            |
 |==============PAGE PAIEMENT UMOJA (Visa/MC)==================>|            |
 |   Saisie      |               |               |              |            |
 |   carte       |               |               |              |            |
 |==============PAIEMENT TRAITE================================>|            |
 |               |               |               |              |            |
 |               |               |               |<---CALLBACK POST---------|
 |               |               |               |  (HMAC signed)           |
 |               |               |               |--Verify HMAC |            |
 |               |               |               |--UPDATE pay->|            |
 |               |               |               |  (completed) |            |
 |               |               |               |--UPDATE sub->|            |
 |               |               |               |  (active)    |            |
 |               |               |               |              |            |
 |               |               |               |--SMS + Email notification |
 |               |               |               |              |            |
 |<--Retour site-|               |               |              |            |
 |               |--GET /api/payments/{id}/status--------------->|           |
 |               |               |               |<--completed--|            |
 |               |<--Abonnement actif!-----------|              |            |
 |<--Dashboard-->|               |               |              |            |
```

### 3.3 Flux Apprentissage (IA)

```
User          Frontend        Nginx LB        Backend        Flask AI      OpenAI
 |               |               |               |              |            |
 |--Demarrer---->|               |               |              |            |
 |  session      |               |               |              |            |
 |               |--POST /api/learning/sessions->|              |            |
 |               |               |               |--POST /generate---------->|
 |               |               |               |              |--GPT-4---->|
 |               |               |               |              |<--Contenu--|
 |               |               |               |<--AI content-|            |
 |               |               |               |--INSERT----->|            |
 |               |               |<--Session + contenu IA-------|            |
 |               |<--Afficher lecon-------------|              |            |
 |<--Lecon IA--->|               |               |              |            |
 |               |               |               |              |            |
 |--Terminer---->|               |               |              |            |
 |  (score=85)   |               |               |              |            |
 |               |--PUT /sessions/{id}/complete->|              |            |
 |               |               |               |--XP + Streak |            |
 |               |               |               |--Carbone     |            |
 |               |               |               |--Badges      |            |
 |               |               |               |--Level up?   |            |
 |               |               |               |--Compensation|            |
 |               |               |<--Resultat complet-----------|            |
 |               |<--Progression + badges--------|              |            |
 |<--Bravo! XP+--|               |               |              |            |
```

---

## 4. Diagramme de deploiement Docker Compose (Production)

```yaml
# docker-compose.prod.yml
version: "3.9"

services:

  # ── Nginx Load Balancer ──────────────────
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/ssl
    depends_on:
      - backend-1
      - backend-2
    restart: always

  # ── Backend Instance 1 ──────────────────
  backend-1:
    build: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      # ... toutes les variables
    expose:
      - "8000"
    restart: always

  # ── Backend Instance 2 ──────────────────
  backend-2:
    build: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      # ... memes variables
    expose:
      - "8000"
    restart: always

  # ── AI Service ──────────────────────────
  ai-service:
    build: ./ai-service
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    expose:
      - "5000"
    restart: always

  # ── Redis (Cache & Sessions) ────────────
  redis:
    image: redis:7-alpine
    expose:
      - "6379"
    volumes:
      - redis_data:/data
    restart: always

volumes:
  redis_data:
```

---

## 5. Securite entre les couches

```
+------------------------------------------------------------------+
|                    MATRICE DE SECURITE                             |
+------------------------------------------------------------------+

 Couche              Protocole       Auth              Chiffrement
 ─────────────────── ─────────────── ────────────────── ──────────
 User -> Cloudflare  HTTPS (TLS 1.3) -                 SSL/TLS
 Cloudflare -> Nginx HTTPS           -                 SSL/TLS
 Nginx -> Frontend   HTTP (interne)  -                 Reseau Docker
 Nginx -> Backend    HTTP (interne)  -                 Reseau Docker
 Frontend -> Backend HTTP + JWT      Bearer Token      JWT signé HS256
 Backend -> MySQL    TCP (3306)      User/Password     PyMySQL + SSL
 Backend -> Redis    TCP (6379)      Password           TLS optionnel
 Backend -> Umoja    HTTPS           HMAC-SHA256        TLS 1.2+
 Backend -> MGT-SMS  HTTPS           x-api-key          TLS 1.2+
 Backend -> Gmail    SMTPS (465)     App Password       SSL/TLS
 Backend -> OpenAI   HTTPS           Bearer API Key     TLS 1.2+
 Umoja -> Backend    HTTPS POST      HMAC Callback      TLS 1.2+
 Donnees en base     -               -                  Fernet AES-128

+------------------------------------------------------------------+
|  DONNEES CHIFFREES EN BASE (Fernet AES-128-CBC + HMAC-SHA256) :  |
|  - date_de_naissance    - nationalite    - numero_piece_identite |
|  - adresse_rue          - ville          - code_postal           |
|  - pays                                                          |
|                                                                   |
|  MOT DE PASSE : bcrypt (hachage irreversible, jamais stocke)    |
+------------------------------------------------------------------+
```

---

## 6. Scalabilite

```
                    STRATEGIE DE MISE A L'ECHELLE
                    =============================

  Charge faible          Charge moyenne          Charge forte
  (< 100 users)         (100-1000 users)        (> 1000 users)
  ──────────────         ────────────────         ──────────────

  1x Nginx               1x Nginx                2x Nginx (HA)
  1x Backend             2x Backend              3-5x Backend
  1x AI Service          1x AI Service           2x AI Service
  MySQL distant          MySQL distant           MySQL cluster
  Pas de Redis           Redis (cache)           Redis cluster
  Pas de CDN             Cloudflare Free         Cloudflare Pro

  Serveur unique         2 serveurs              3+ serveurs
  $5-10/mois             $20-40/mois             $100+/mois
```

---

## 7. Monitoring & Observabilite (implemente)

```
+------------------------------------------------------------------+
|                    STACK MONITORING                                |
|                    (Docker Compose - 5 services)                   |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+  +------------------+                       |
|  | Prometheus       |  | Grafana          |                       |
|  | :9090            |  | :3000            |                       |
|  | (Metriques)      |  | (Dashboards)     |                       |
|  |                  |  |                  |                       |
|  | Scrape : 15s     |  | Login : admin    |                       |
|  | Retention : 30j  |  | Password : ***   |                       |
|  | 14 alertes       |  | Dashboard auto-  |                       |
|  |                  |  | provisionne      |                       |
|  +-------+----------+  +--------+---------+                       |
|          |                       |                                |
|          | Scrape targets :      | Datasource :                   |
|          |                       | Prometheus                     |
|  +-------v----------+  +--------v---------+  +------------------+ |
|  | Backend FastAPI   |  | Redis Exporter   |  | Node Exporter    | |
|  | /metrics :8000    |  | :9121            |  | :9100            | |
|  |                  |  |                  |  |                  | |
|  | - HTTP req/sec   |  | - Memoire Redis  |  | - CPU %          | |
|  | - Latence P50/95 |  | - Hits / Misses  |  | - RAM %          | |
|  | - Erreurs 5xx    |  | - Connexions     |  | - Disque %       | |
|  | - Endpoints      |  | - Evictions      |  | - Reseau         | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+                       |
|  | MySQL Exporter   |  | Backend Monitoring|                      |
|  | :9104            |  | /api/monitoring   |                      |
|  |                  |  |                  |                       |
|  | - Connexions SQL |  | /health (public) |                      |
|  | - QPS            |  | /system (admin)  |                      |
|  | - Slow queries   |  | /redis (admin)   |                      |
|  | - Taille tables  |  | /database (admin)|                      |
|  +------------------+  | /backup (admin)  |                      |
|                        | /cache/flush     |                      |
|                        +------------------+                       |
+------------------------------------------------------------------+
```

### Alertes Prometheus configurees (14 regles)

| Alerte | Seuil | Severite | Delai |
|--------|-------|----------|-------|
| BackendDown | up == 0 | CRITICAL | 1 min |
| HighErrorRate | 5xx > 5% | WARNING | 5 min |
| HighLatency | P95 > 2s | WARNING | 5 min |
| RedisDown | up == 0 | CRITICAL | 1 min |
| RedisHighMemory | > 85% | WARNING | 5 min |
| RedisTooManyConnections | > 100 | WARNING | 5 min |
| RedisHighEviction | > 10/s | WARNING | 5 min |
| MySQLDown | up == 0 | CRITICAL | 1 min |
| MySQLHighConnections | > 80% | WARNING | 5 min |
| MySQLSlowQueries | > 0.5/s | WARNING | 10 min |
| HighCPUUsage | > 85% | WARNING | 10 min |
| HighMemoryUsage | > 90% | CRITICAL | 5 min |
| DiskSpaceLow | > 85% | WARNING | 10 min |
| DiskSpaceCritical | > 95% | CRITICAL | 5 min |

---

## 8. Redis - Couche Cache

```
+------------------------------------------------------------------+
|                        REDIS 7.2                                  |
+------------------------------------------------------------------+
|                                                                   |
|  Configuration :                                                  |
|  - Memoire max : 256 Mo                                          |
|  - Politique eviction : allkeys-lru                              |
|  - Persistence : AOF (sync chaque seconde) + Snapshots           |
|  - Mot de passe : EcoLearn@Redis2026                             |
|                                                                   |
|  Cles de cache :                                                 |
|  +-----------------------------+--------+------------------------+|
|  | Cle                         | TTL    | Usage                  ||
|  +-----------------------------+--------+------------------------+|
|  | ecolearnai:plans:active     | 10 min | Plans d'abonnement     ||
|  | ecolearnai:admin:dashboard  |  2 min | Dashboard admin        ||
|  | ecolearnai:dashboard:user:* |  3 min | Dashboard utilisateur  ||
|  | ecolearnai:otp_attempts:*   | 15 min | Anti brute-force OTP   ||
|  | ecolearnai:ratelimit:*      |  1 min | Rate limiting API      ||
|  +-----------------------------+--------+------------------------+|
|                                                                   |
|  Mode degrade : si Redis est down, l'app continue sans cache.   |
+------------------------------------------------------------------+
```

---

## 9. Cron Backup - Replication automatique

```
+------------------------------------------------------------------+
|                    REPLICATION QUOTIDIENNE                         |
|                    Chaque jour a 01:00 UTC                        |
+------------------------------------------------------------------+
|                                                                   |
|  APScheduler (dans le backend FastAPI)                           |
|       |                                                           |
|       | Pour chaque table (10 tables) :                          |
|       | 1. SELECT * (source)                                     |
|       | 2. DELETE (backup)                                       |
|       | 3. INSERT par lots de 500 (backup)                       |
|       |                                                           |
|  +----------+           +----------+                              |
|  | MySQL    |  -------> | MySQL    |                              |
|  | PRINCIPAL|  copie    | BACKUP   |                              |
|  | .54:3306 |  complete | .55:3306 |                              |
|  +----------+           +----------+                              |
|                                                                   |
|  En cas d'echec : alerte email a l'administrateur                |
|  Historique : 30 derniers backups conserves en memoire            |
|  Statut consultable : GET /api/monitoring/backup                 |
+------------------------------------------------------------------+
```

---

## 10. Resume des ports et services

| Service | Port | Type | Description |
|---------|------|------|-------------|
| Nginx LB | 80, 443 | Externe | Load Balancer / Reverse Proxy |
| Backend API | 8000 | Externe | FastAPI (Python) |
| AI Service (Flask) | 5000 | Interne | Flask + OpenAI GPT |
| Redis | 6379 | Interne | Cache + Rate Limiting |
| MySQL Principal | 3306 | Distant | 159.89.13.54 |
| MySQL Backup | 3306 | Distant | 159.89.13.55 |
| Prometheus | 9090 | Interne | Collecte metriques |
| Grafana | 3000 | Externe | Dashboards visuels |
| Node Exporter | 9100 | Interne | Metriques OS |
| Redis Exporter | 9121 | Interne | Metriques Redis |
| MySQL Exporter | 9104 | Interne | Metriques MySQL |
| Umoja CardAPI | 443 | Externe | API paiement carte |
| MGT-SMS API | 443 | Externe | Envoi SMS / OTP |
| Gmail SMTP | 465 | Externe | Envoi emails |
| OpenAI API | 443 | Externe | Generation contenu IA |

### Docker Compose : 8 services

```bash
docker compose up -d
# Services : backend, ai-service, redis, prometheus, grafana,
#            node-exporter, redis-exporter, mysql-exporter
```

---

*Document genere le 11/02/2026 - EcoLearn AI v1.4.0*
