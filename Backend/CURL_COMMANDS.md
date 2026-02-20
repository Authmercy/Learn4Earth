# EcoLearn AI - Guide Complet des Commandes cURL

**Base URL** : `http://206.189.56.166:8000`
**Version** : 1.5.0
**Date** : 11/02/2026

---

## Table des matieres

1. [Variable TOKEN (a configurer d'abord)](#1-variable-token)
2. [Root & Health](#2-root--health)
3. [Authentification](#3-authentification)
4. [Utilisateurs & Profil](#4-utilisateurs--profil)
5. [RGPD / Donnees Personnelles](#5-rgpd--donnees-personnelles)
6. [Abonnements](#6-abonnements)
7. [Paiements & Factures](#7-paiements--factures)
8. [Apprentissage](#8-apprentissage)
9. [Empreinte Carbone](#9-empreinte-carbone)
10. [Tableau de Bord](#10-tableau-de-bord)
11. [Administration](#11-administration)
12. [Monitoring & Cache](#12-monitoring--cache)
13. [Chatbot IA](#13-chatbot-ia)
14. [Cours Video](#14-cours-video)

---

## 1. Variable TOKEN

Avant d'utiliser les endpoints proteges, obtenez un token et stockez-le dans une variable :

```bash
# Remplacez email et mot de passe par les votres
TOKEN=$(curl -s -X POST 'http://206.189.56.166:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo $TOKEN
```

Tous les endpoints ci-dessous utilisent `$TOKEN`. Si vous preferez, remplacez `$TOKEN` par le token copie-colle.

---

## 2. Root & Health

### Informations API

```bash
curl -X GET 'http://206.189.56.166:8000/'
```

### Health Check simple

```bash
curl -X GET 'http://206.189.56.166:8000/health'
```

### Metriques Prometheus

```bash
curl -X GET 'http://206.189.56.166:8000/metrics'
```

---

## 3. Authentification

### 3.1 Creer le premier admin (une seule fois)

```bash
curl -X POST 'http://206.189.56.166:8000/api/admin/seed-admin' \
  -H 'Content-Type: application/json'
```

### 3.2 Inscription d'un utilisateur

```bash
curl -X POST 'http://206.189.56.166:8000/api/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "jean.dupont@email.com",
  "password": "MonPass@2026!",
  "full_name": "Jean Dupont",
  "phone_number": "+243898900119",
  "date_of_birth": "1990-05-15",
  "address_line": "12 Avenue de la Paix",
  "address_city": "Kinshasa",
  "address_postal_code": "00243",
  "address_country": "RDC",
  "level": "debutant",
  "objectives": "Apprendre Python",
  "preferences": "videos,exercices",
  "gdpr_consent": true,
  "gdpr_marketing_consent": false,
  "gdpr_data_retention_consent": true
}'
```

> Un code OTP sera envoye par SMS et par email.

### 3.3 Verifier le code OTP (SMS ou Email)

```bash
curl -X POST 'http://206.189.56.166:8000/api/auth/verify-sms' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "jean.dupont@email.com",
  "code": "482917"
}'
```

### 3.4 Renvoyer un code OTP

```bash
curl -X POST 'http://206.189.56.166:8000/api/auth/resend-otp' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "jean.dupont@email.com"
}'
```

### 3.5 Connexion (obtenir le token JWT)

```bash
curl -X POST 'http://206.189.56.166:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=jean.dupont@email.com&password=MonPass@2026!'
```

> **IMPORTANT** : Le login utilise `application/x-www-form-urlencoded` (pas JSON).
> Le champ s'appelle `username` mais contient l'email.

### 3.6 Connexion admin

```bash
curl -X POST 'http://206.189.56.166:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!'
```

---

## 4. Utilisateurs & Profil

### 4.1 Voir mon profil

```bash
curl -X GET 'http://206.189.56.166:8000/api/users/me' \
  -H 'Authorization: Bearer '$TOKEN
```

### 4.2 Modifier mon profil

```bash
curl -X PUT 'http://206.189.56.166:8000/api/users/me' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "full_name": "Jean-Pierre Dupont",
  "bio": "Developpeur passione par l ecologie",
  "language": "fr",
  "timezone": "Africa/Kinshasa",
  "avatar_url": "https://example.com/avatar.jpg",
  "objectives": "Maitriser Python et le machine learning",
  "preferences": "videos,exercices,quiz"
}'
```

### 4.3 Modifier les donnees sensibles (chiffrees RGPD)

```bash
curl -X PUT 'http://206.189.56.166:8000/api/users/me' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "address_line": "25 Boulevard du 30 Juin",
  "address_city": "Kinshasa",
  "address_postal_code": "00243",
  "address_country": "RDC",
  "date_of_birth": "1990-05-15"
}'
```

### 4.4 Changer le mot de passe

```bash
curl -X PUT 'http://206.189.56.166:8000/api/users/me/password' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "current_password": "Admin@2026!",
  "new_password": "YAN@mol123456"
}'
```

### 4.5 Voir ma progression

```bash
curl -X GET 'http://206.189.56.166:8000/api/users/me/progression' \
  -H 'Authorization: Bearer '$TOKEN
```

### 4.6 Voir mes badges

```bash
curl -X GET 'http://206.189.56.166:8000/api/users/me/achievements' \
  -H 'Authorization: Bearer '$TOKEN
```

### 4.7 Desactiver mon compte

```bash
curl -X PUT 'http://206.189.56.166:8000/api/users/me/deactivate' \
  -H 'Authorization: Bearer '$TOKEN
```

---

## 5. RGPD / Donnees Personnelles

### 5.1 Exporter toutes mes donnees (droit a la portabilite)

```bash
curl -X GET 'http://206.189.56.166:8000/api/users/me/data-export' \
  -H 'Authorization: Bearer '$TOKEN
```

> Retourne TOUTES les donnees personnelles dechiffrees (Article 20 RGPD).

### 5.2 Modifier mes consentements RGPD

```bash
curl -X PUT 'http://206.189.56.166:8000/api/users/me/gdpr-consent' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "gdpr_marketing_consent": true,
  "gdpr_data_retention_consent": false
}'
```

### 5.3 Voir les informations de confidentialite

```bash
curl -X GET 'http://206.189.56.166:8000/api/users/me/privacy-info' \
  -H 'Authorization: Bearer '$TOKEN
```

### 5.4 Supprimer mon compte (droit a l'effacement)

```bash
curl -X DELETE 'http://206.189.56.166:8000/api/users/me' \
  -H 'Authorization: Bearer '$TOKEN
```

> **ATTENTION** : Suppression definitive et irreversible de toutes les donnees (Article 17 RGPD).

---

## 6. Abonnements

### 6.1 Voir les plans disponibles (public)

```bash
curl -X GET 'http://206.189.56.166:8000/api/subscriptions/plans'
```

### 6.2 Souscrire un abonnement (Mobile Money)

```bash
curl -X POST 'http://206.189.56.166:8000/api/subscriptions/subscribe' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "plan": "mensuel",
  "payment_method": "mobile_money"
}'
```

### 6.3 Souscrire un abonnement (Carte bancaire)

```bash
curl -X POST 'http://206.189.56.166:8000/api/subscriptions/subscribe' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "plan": "annuel",
  "payment_method": "carte_bancaire"
}'
```

> Retourne `payment_url` : URL de redirection vers la page de paiement Moko/FreshPay.

### 6.4 Voir mes abonnements

```bash
curl -X GET 'http://206.189.56.166:8000/api/subscriptions/my' \
  -H 'Authorization: Bearer '$TOKEN
```

---

## 7. Paiements & Factures

### 7.1 Lister mes paiements

```bash
curl -X GET 'http://206.189.56.166:8000/api/payments/my' \
  -H 'Authorization: Bearer '$TOKEN
```

### 7.2 Voir une facture

```bash
# Remplacer {payment_id} par l'UUID du paiement
curl -X GET 'http://206.189.56.166:8000/api/payments/{payment_id}/invoice' \
  -H 'Authorization: Bearer '$TOKEN
```

### 7.3 Verifier le statut d'un paiement (polling carte bancaire)

```bash
# Remplacer {payment_id} par l'UUID du paiement
curl -X GET 'http://206.189.56.166:8000/api/payments/{payment_id}/status' \
  -H 'Authorization: Bearer '$TOKEN
```

> Appeler toutes les 3 secondes apres redirection Moko, jusqu'a `status: completed` ou `failed`.

---

## 8. Apprentissage

> **IMPORTANT** : Les endpoints `POST /api/learning/paths` et `POST /api/learning/sessions` necessitent un **abonnement actif**. Sans abonnement, vous recevrez `403 Forbidden`. Souscrivez d'abord via la section 6.

### 8.1 Creer un parcours d'apprentissage

```bash
curl -X POST 'http://206.189.56.166:8000/api/learning/paths' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Python pour debutants",
  "subject": "python",
  "description": "Apprendre les bases de Python",
  "difficulty": "debutant",
  "total_sessions": 5
}'
```

### 8.2 Lister mes parcours

```bash
curl -X GET 'http://206.189.56.166:8000/api/learning/paths' \
  -H 'Authorization: Bearer '$TOKEN
```

### 8.3 Voir un parcours specifique

```bash
# Remplacer {path_id} par l'UUID du parcours
curl -X GET 'http://206.189.56.166:8000/api/learning/paths/{path_id}' \
  -H 'Authorization: Bearer '$TOKEN
```

### 8.4 Demarrer une session (genere le contenu IA)

```bash
# Remplacer {path_id} par l'UUID du parcours
curl -X POST 'http://206.189.56.166:8000/api/learning/sessions' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "learning_path_id": "{path_id}",
  "title": "Introduction aux variables"
}'
```

### 8.5 Terminer une session

```bash
# Remplacer {session_id} par l'UUID de la session
curl -X PUT 'http://206.189.56.166:8000/api/learning/sessions/{session_id}/complete' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "score": 85.0,
  "duration_minutes": 25.5
}'
```

> Declenche automatiquement : calcul XP, streak, niveau, badges, empreinte carbone, compensation eco.

### 8.6 Lister mes sessions

```bash
curl -X GET 'http://206.189.56.166:8000/api/learning/sessions' \
  -H 'Authorization: Bearer '$TOKEN
```

---

## 9. Empreinte Carbone

### 9.1 Resume carbone

```bash
curl -X GET 'http://206.189.56.166:8000/api/carbon/summary' \
  -H 'Authorization: Bearer '$TOKEN
```

### 9.2 Lister les empreintes par session

```bash
curl -X GET 'http://206.189.56.166:8000/api/carbon/footprints' \
  -H 'Authorization: Bearer '$TOKEN
```

### 9.3 Lister les compensations ecologiques

```bash
curl -X GET 'http://206.189.56.166:8000/api/carbon/compensations' \
  -H 'Authorization: Bearer '$TOKEN
```

---

## 10. Tableau de Bord

### Dashboard utilisateur (toutes les stats en un appel)

```bash
curl -X GET 'http://206.189.56.166:8000/api/dashboard/' \
  -H 'Authorization: Bearer '$TOKEN
```

> Contient : progression, XP, streak, badges, carbone, compensations.

---

## 11. Administration

> **Prerequis** : Etre connecte avec un compte `admin` ou `super_admin`.

### 11.1 Initialiser le premier admin

```bash
curl -X POST 'http://206.189.56.166:8000/api/admin/seed-admin' \
  -H 'Content-Type: application/json'
```

> **Ne fonctionne qu'une seule fois.** Retourne email=`admin@ecolearnai.com` et password=`Admin@2026!`

---

### Plans d'abonnement

### 11.2 Creer le plan mensuel

```bash
curl -X POST 'http://206.189.56.166:8000/api/admin/plans' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "code": "mensuel",
  "name": "Abonnement Mensuel",
  "description": "Acces complet pendant 30 jours",
  "price": 9.99,
  "currency": "USD",
  "duration_days": 30,
  "is_active": true,
  "sort_order": 1
}'
```

### 11.3 Creer le plan annuel

```bash
curl -X POST 'http://206.189.56.166:8000/api/admin/plans' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "code": "annuel",
  "name": "Abonnement Annuel",
  "description": "Acces complet pendant 1 an - Economisez 30%",
  "price": 89.99,
  "currency": "USD",
  "duration_days": 365,
  "is_active": true,
  "sort_order": 2
}'
```

### 11.4 Creer le plan trimestriel

```bash
curl -X POST 'http://206.189.56.166:8000/api/admin/plans' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "code": "trimestriel",
  "name": "Abonnement Trimestriel",
  "description": "Acces complet pendant 3 mois",
  "price": 24.99,
  "currency": "USD",
  "duration_days": 90,
  "is_active": true,
  "sort_order": 3
}'
```

### 11.5 Lister tous les plans

```bash
# Plans actifs uniquement
curl -X GET 'http://206.189.56.166:8000/api/admin/plans' \
  -H 'Authorization: Bearer '$TOKEN

# Inclure les plans desactives
curl -X GET 'http://206.189.56.166:8000/api/admin/plans?include_inactive=true' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.6 Voir un plan specifique

```bash
# Remplacer {plan_id} par l'UUID du plan
curl -X GET 'http://206.189.56.166:8000/api/admin/plans/{plan_id}' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.7 Modifier le prix d'un plan

```bash
# Remplacer {plan_id} par l'UUID du plan
curl -X PUT 'http://206.189.56.166:8000/api/admin/plans/{plan_id}' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "price": 12.99
}'
```

### 11.8 Modifier plusieurs champs d'un plan

```bash
# Remplacer {plan_id} par l'UUID du plan
curl -X PUT 'http://206.189.56.166:8000/api/admin/plans/{plan_id}' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Abonnement Premium Mensuel",
  "price": 14.99,
  "description": "Acces illimite + support prioritaire",
  "max_sessions_per_day": 10
}'
```

### 11.9 Supprimer / Desactiver un plan

```bash
# Remplacer {plan_id} par l'UUID du plan
curl -X DELETE 'http://206.189.56.166:8000/api/admin/plans/{plan_id}' \
  -H 'Authorization: Bearer '$TOKEN
```

---

### Gestion des utilisateurs

### 11.10 Lister les utilisateurs

```bash
# Page 1, 20 par page
curl -X GET 'http://206.189.56.166:8000/api/admin/users?page=1&per_page=20' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.11 Rechercher un utilisateur

```bash
curl -X GET 'http://206.189.56.166:8000/api/admin/users?search=dupont' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.12 Filtrer par role

```bash
# Tous les admins
curl -X GET 'http://206.189.56.166:8000/api/admin/users?role=admin' \
  -H 'Authorization: Bearer '$TOKEN

# Tous les utilisateurs standard
curl -X GET 'http://206.189.56.166:8000/api/admin/users?role=user' \
  -H 'Authorization: Bearer '$TOKEN

# Utilisateurs desactives
curl -X GET 'http://206.189.56.166:8000/api/admin/users?is_active=false' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.13 Voir le detail d'un utilisateur

```bash
# Remplacer {user_id} par l'UUID de l'utilisateur
curl -X GET 'http://206.189.56.166:8000/api/admin/users/{user_id}' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.14 Changer le role d'un utilisateur (super_admin uniquement)

```bash
# Promouvoir en admin
curl -X PUT 'http://206.189.56.166:8000/api/admin/users/{user_id}/role' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "role": "admin"
}'

# Promouvoir en super_admin
curl -X PUT 'http://206.189.56.166:8000/api/admin/users/{user_id}/role' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "role": "super_admin"
}'

# Revoquer les droits admin
curl -X PUT 'http://206.189.56.166:8000/api/admin/users/{user_id}/role' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "role": "user"
}'
```

### 11.15 Desactiver un utilisateur

```bash
# Remplacer {user_id} par l'UUID de l'utilisateur
curl -X PUT 'http://206.189.56.166:8000/api/admin/users/{user_id}/deactivate' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.16 Reactiver un utilisateur

```bash
# Remplacer {user_id} par l'UUID de l'utilisateur
curl -X PUT 'http://206.189.56.166:8000/api/admin/users/{user_id}/activate' \
  -H 'Authorization: Bearer '$TOKEN
```

---

### Paiements (vue admin)

### 11.17 Lister tous les paiements

```bash
curl -X GET 'http://206.189.56.166:8000/api/admin/payments' \
  -H 'Authorization: Bearer '$TOKEN
```

### 11.18 Filtrer les paiements

```bash
# Paiements reussis uniquement
curl -X GET 'http://206.189.56.166:8000/api/admin/payments?status=completed' \
  -H 'Authorization: Bearer '$TOKEN

# Paiements echoues
curl -X GET 'http://206.189.56.166:8000/api/admin/payments?status=failed' \
  -H 'Authorization: Bearer '$TOKEN

# Paiements en attente
curl -X GET 'http://206.189.56.166:8000/api/admin/payments?status=pending' \
  -H 'Authorization: Bearer '$TOKEN

# Par methode de paiement
curl -X GET 'http://206.189.56.166:8000/api/admin/payments?payment_method=carte_bancaire' \
  -H 'Authorization: Bearer '$TOKEN

curl -X GET 'http://206.189.56.166:8000/api/admin/payments?payment_method=mobile_money' \
  -H 'Authorization: Bearer '$TOKEN

# Pagination
curl -X GET 'http://206.189.56.166:8000/api/admin/payments?page=2&per_page=10' \
  -H 'Authorization: Bearer '$TOKEN
```

---

### Dashboard Admin

### 11.19 Voir le dashboard admin (toutes les stats)

```bash
curl -X GET 'http://206.189.56.166:8000/api/admin/dashboard' \
  -H 'Authorization: Bearer '$TOKEN
```

> Retourne : utilisateurs, abonnements, revenus, paiements, apprentissage, ecologie.

---

## 13. Chatbot IA

### 13.1 Envoyer un message au chatbot (nouvelle conversation)
```bash
curl -X POST 'http://206.189.56.166:8000/api/chatbot/send' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "Comment apprendre Python efficacement ?"
}'
```

### 13.2 Envoyer un message dans une conversation existante
```bash
curl -X POST 'http://206.189.56.166:8000/api/chatbot/send' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "Et pour le machine learning ?",
  "conversation_id": "{conversation_id}"
}'
```

### 13.3 Lister mes conversations
```bash
curl -X GET 'http://206.189.56.166:8000/api/chatbot/conversations' \
  -H 'Authorization: Bearer '$TOKEN
```

### 13.4 Voir l'historique d'une conversation
```bash
curl -X GET 'http://206.189.56.166:8000/api/chatbot/conversations/{conversation_id}' \
  -H 'Authorization: Bearer '$TOKEN
```

### 13.5 Supprimer une conversation (RGPD)
```bash
curl -X DELETE 'http://206.189.56.166:8000/api/chatbot/conversations/{conversation_id}' \
  -H 'Authorization: Bearer '$TOKEN
```

> Le chatbot est accessible a **tous les utilisateurs authentifies**, meme sans abonnement.

---

## Flux complet d'utilisation (exemple)

```bash
# ── 1. Initialiser l'admin (une seule fois) ──
curl -s -X POST 'http://206.189.56.166:8000/api/admin/seed-admin'

# ── 2. Login admin ──
TOKEN=$(curl -s -X POST 'http://206.189.56.166:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# ── 3. Creer les plans d'abonnement ──
curl -s -X POST 'http://206.189.56.166:8000/api/admin/plans' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"code":"mensuel","name":"Mensuel","price":9.99,"currency":"USD","duration_days":30,"sort_order":1}'

curl -s -X POST 'http://206.189.56.166:8000/api/admin/plans' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"code":"annuel","name":"Annuel","price":89.99,"currency":"USD","duration_days":365,"sort_order":2}'

# ── 4. Inscrire un utilisateur ──
curl -s -X POST 'http://206.189.56.166:8000/api/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "email":"test@example.com","password":"Test@2026!",
    "full_name":"Test User","phone_number":"+243000000001",
    "date_of_birth":"1995-01-01","gdpr_consent":true
  }'

# ── 5. Verifier le code OTP (recu par SMS/Email) ──
curl -s -X POST 'http://206.189.56.166:8000/api/auth/verify-sms' \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","code":"123456"}'

# ── 6. Login utilisateur ──
USER_TOKEN=$(curl -s -X POST 'http://206.189.56.166:8000/api/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test@example.com&password=Test@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# ── 7. S'abonner (requis avant de creer des parcours/sessions) ──
curl -s -X POST 'http://206.189.56.166:8000/api/subscriptions/subscribe' \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"plan":"mensuel","payment_method":"mobile_money"}'

# ── 7b. Tester le chatbot (accessible sans abonnement) ──
curl -s -X POST 'http://206.189.56.166:8000/api/chatbot/send' \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Bonjour, comment fonctionne la plateforme ?"}'

# ── 8. Creer un parcours ──
PATH_RESPONSE=$(curl -s -X POST 'http://206.189.56.166:8000/api/learning/paths' \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Python Bases","subject":"python","total_sessions":3}')
echo $PATH_RESPONSE

# ── 9. Demarrer une session ──
# Remplacer PATH_ID par l'id retourne ci-dessus
curl -s -X POST 'http://206.189.56.166:8000/api/learning/sessions' \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"learning_path_id":"PATH_ID","title":"Variables et types"}'

# ── 10. Terminer la session ──
# Remplacer SESSION_ID par l'id retourne ci-dessus
curl -s -X PUT 'http://206.189.56.166:8000/api/learning/sessions/SESSION_ID/complete' \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"score":90,"duration_minutes":20}'

# ── 11. Voir le dashboard ──
curl -s -X GET 'http://206.189.56.166:8000/api/dashboard/' \
  -H "Authorization: Bearer $USER_TOKEN"

# ── 12. Dashboard admin ──
curl -s -X GET 'http://206.189.56.166:8000/api/admin/dashboard' \
  -H "Authorization: Bearer $TOKEN"
```

---

## 12. Monitoring & Cache

### Health check detaille (tous les composants - public)

```bash
curl -X GET 'http://206.189.56.166:8000/api/monitoring/health'
```

### Metriques systeme (CPU, RAM, Disque - admin)

```bash
curl -X GET 'http://206.189.56.166:8000/api/monitoring/system' \
  -H "Authorization: Bearer $TOKEN"
```

### Statistiques Redis (admin)

```bash
curl -X GET 'http://206.189.56.166:8000/api/monitoring/redis' \
  -H "Authorization: Bearer $TOKEN"
```

### Informations base de donnees (admin)

```bash
curl -X GET 'http://206.189.56.166:8000/api/monitoring/database' \
  -H "Authorization: Bearer $TOKEN"
```

### Statut du backup automatique (admin)

```bash
curl -X GET 'http://206.189.56.166:8000/api/monitoring/backup' \
  -H "Authorization: Bearer $TOKEN"
```

### Vider le cache Redis (admin)

```bash
curl -X POST 'http://206.189.56.166:8000/api/monitoring/cache/flush' \
  -H "Authorization: Bearer $TOKEN"
```

---

## 14. Cours Video

### 14.1 Catalogue de videos (avec filtres et pagination)

```bash
# Toutes les videos publiees
curl -X GET 'http://206.189.56.166:8000/api/videos/catalog' \
  -H "Authorization: Bearer $TOKEN"
```

```bash
# Filtrer par sujet
curl -X GET 'http://206.189.56.166:8000/api/videos/catalog?subject=Python' \
  -H "Authorization: Bearer $TOKEN"
```

```bash
# Filtrer par categorie et difficulte
curl -X GET 'http://206.189.56.166:8000/api/videos/catalog?category=Programmation&difficulty=debutant' \
  -H "Authorization: Bearer $TOKEN"
```

```bash
# Rechercher dans titre/description/tags
curl -X GET 'http://206.189.56.166:8000/api/videos/catalog?search=python' \
  -H "Authorization: Bearer $TOKEN"
```

```bash
# Videos gratuites uniquement
curl -X GET 'http://206.189.56.166:8000/api/videos/catalog?is_free=true' \
  -H "Authorization: Bearer $TOKEN"
```

```bash
# Pagination (page 2, 6 videos par page)
curl -X GET 'http://206.189.56.166:8000/api/videos/catalog?page=2&per_page=6' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.2 Sujets disponibles

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/subjects' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.3 Categories disponibles

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/categories' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.4 Detail d'une video (avec progression)

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/{video_id}' \
  -H "Authorization: Bearer $TOKEN"
```

> **Note** : Retourne la video + la progression de l'utilisateur. Incremente le compteur de vues. Retourne `403` si la video requiert un abonnement et que l'utilisateur n'en a pas.

### 14.5 Mettre a jour la progression de lecture

```bash
# Sauvegarder la position (envoyer toutes les 10 secondes depuis le lecteur)
curl -X PUT 'http://206.189.56.166:8000/api/videos/{video_id}/progress' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"watched_seconds": 720}'
```

> **Gamification** : Quand la progression atteint >= 90%, la video est marquee terminee et l'utilisateur recoit **+15 XP**.

### 14.6 Recuperer la progression sur une video

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/{video_id}/progress' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.7 Historique des videos regardees

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/me/history' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.8 Admin : Creer une video YouTube

```bash
curl -X POST 'http://206.189.56.166:8000/api/videos/admin/create' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction a Python - Les bases",
    "description": "Apprenez les fondamentaux de Python : variables, types, conditions, boucles",
    "subject": "Python",
    "category": "Programmation",
    "difficulty": "debutant",
    "tags": "python,programmation,debutant",
    "video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
    "video_type": "youtube",
    "thumbnail_url": "https://img.youtube.com/vi/rfscVS0vtbw/maxresdefault.jpg",
    "duration_seconds": 14400,
    "is_free": true,
    "is_published": true
  }'
```

### 14.9 Admin : Creer une video Vimeo (abonnement requis)

```bash
curl -X POST 'http://206.189.56.166:8000/api/videos/admin/create' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deep Learning avec TensorFlow",
    "description": "Cours avance sur les reseaux de neurones profonds",
    "subject": "Intelligence Artificielle",
    "category": "Programmation",
    "difficulty": "avance",
    "video_url": "https://vimeo.com/123456789",
    "video_type": "vimeo",
    "duration_seconds": 5400,
    "is_free": false,
    "is_published": true,
    "requires_subscription": true
  }'
```

### 14.10 Admin : Creer une video externe (URL directe)

```bash
curl -X POST 'http://206.189.56.166:8000/api/videos/admin/create' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Recyclage des dechets electroniques",
    "description": "Comment recycler correctement vos appareils electroniques",
    "subject": "Ecologie",
    "category": "Environnement",
    "difficulty": "debutant",
    "video_url": "https://cdn.example.com/videos/recyclage.mp4",
    "video_type": "external",
    "duration_seconds": 900,
    "is_free": true,
    "is_published": true
  }'
```

### 14.11 Admin : Uploader un fichier video

```bash
curl -X POST 'http://206.189.56.166:8000/api/videos/admin/upload?title=Mon%20cours&subject=Python&difficulty=debutant&is_free=true&is_published=true' \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/chemin/vers/video.mp4" \
  -F "thumbnail=@/chemin/vers/vignette.jpg"
```

> **Formats acceptes** : mp4, webm, mkv, avi, mov. **Taille max** : 500 Mo.

### 14.12 Admin : Modifier une video

```bash
curl -X PUT 'http://206.189.56.166:8000/api/videos/admin/{video_id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Titre mis a jour",
    "is_published": true,
    "requires_subscription": false
  }'
```

### 14.13 Admin : Supprimer une video

```bash
curl -X DELETE 'http://206.189.56.166:8000/api/videos/admin/{video_id}' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.14 Admin : Lister toutes les videos (y compris non publiees)

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/admin/list?include_unpublished=true' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.15 Admin : Statistiques des videos

```bash
curl -X GET 'http://206.189.56.166:8000/api/videos/admin/stats' \
  -H "Authorization: Bearer $TOKEN"
```

### 14.16 Servir un fichier uploade (streaming)

```bash
# Pas d'authentification requise pour le streaming
curl -X GET 'http://206.189.56.166:8000/api/videos/stream/{filename}'
```

---

## Notes importantes

1. **Token** : Le JWT expire apres **30 minutes**. Re-authentifiez-vous si vous recevez `401 Not authenticated`.
2. **Login** : Le seul endpoint qui utilise `application/x-www-form-urlencoded`. Tous les autres utilisent `application/json`.
3. **Swagger** : Interface interactive disponible sur `http://206.189.56.166:8000/docs`
4. **ReDoc** : Documentation alternative sur `http://206.189.56.166:8000/redoc`
5. **UUID** : Tous les `{user_id}`, `{plan_id}`, `{payment_id}`, `{path_id}`, `{session_id}` sont des UUID v4 (ex: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).
6. **Roles** : `user` (defaut), `admin` (gestion), `super_admin` (tous les droits).
7. **OTP** : Le code de verification est envoye par SMS **et** par email (meme code sur les 2 canaux).
8. **Mot de passe** : Min 8 chars, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractere special.
9. **Cache Redis** : Les dashboards sont caches (admin: 2min, user: 3min). Utiliser `POST /api/monitoring/cache/flush` pour forcer le rafraichissement.
10. **Grafana** : Dashboard visuel sur `http://206.189.56.166:3000` (admin / EcoLearn@Grafana2026).
11. **Backup** : Replication automatique chaque jour a 01:00 UTC vers `ecolearnai_db_backup`.
12. **5 cours gratuits** : Chaque nouvel utilisateur dispose de **5 cours gratuits** pour tester la plateforme. Apres epuisement, un abonnement actif est requis pour `POST /api/learning/paths` et `POST /api/learning/sessions`.
13. **Chatbot** : Accessible a tous les utilisateurs authentifies, meme sans abonnement. Le chatbot repond aux questions generales et invite les non-abonnes a souscrire.
14. **Cours Video** : 4 types de videos supportes (YouTube, Vimeo, Upload, Externe). Les videos gratuites (`is_free=true`) sont accessibles sans abonnement. Les autres requierent un abonnement actif.
15. **Progression Video** : Envoyer `PUT /api/videos/{id}/progress` toutes les 10 secondes pour sauvegarder la position de lecture. Completion a >= 90% → +15 XP.
16. **Upload Video** : Max 500 Mo, formats mp4/webm/mkv/avi/mov. Utiliser `multipart/form-data` pour l'upload.

---


