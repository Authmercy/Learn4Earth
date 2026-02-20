# EcoLearn AI - Documentation Cours Video

**Base URL Production** : `http://206.189.56.166:8000`

---

## Table des matieres

1. [Presentation generale](#1-presentation-generale)
2. [Architecture technique](#2-architecture-technique)
3. [Modeles de donnees](#3-modeles-de-donnees)
4. [Endpoints API - Utilisateurs](#4-endpoints-api---utilisateurs)
   - [Catalogue de videos](#41-catalogue-de-videos)
   - [Sujets disponibles](#42-sujets-disponibles)
   - [Categories disponibles](#43-categories-disponibles)
   - [Detail d'une video](#44-detail-dune-video)
   - [Mettre a jour la progression](#45-mettre-a-jour-la-progression)
   - [Recuperer la progression](#46-recuperer-la-progression)
   - [Historique des videos regardees](#47-historique-des-videos-regardees)
5. [Endpoints API - Administration](#5-endpoints-api---administration)
   - [Creer une video (URL)](#51-creer-une-video-url)
   - [Uploader un fichier video](#52-uploader-un-fichier-video)
   - [Modifier une video](#53-modifier-une-video)
   - [Supprimer une video](#54-supprimer-une-video)
   - [Lister toutes les videos](#55-lister-toutes-les-videos-admin)
   - [Statistiques videos](#56-statistiques-videos)
6. [Types de videos supportes](#6-types-de-videos-supportes)
7. [Systeme de progression et XP](#7-systeme-de-progression-et-xp)
8. [Controle d'acces](#8-controle-dacces)
9. [Commandes cURL completes](#9-commandes-curl-completes)
10. [Integration Frontend](#10-integration-frontend)
11. [Gestion des erreurs](#11-gestion-des-erreurs)

---

## 1. Presentation generale

Le module **Cours Video** permet aux administrateurs de publier des contenus video pedagogiques et aux utilisateurs de les consulter avec un suivi de progression.

### Fonctionnalites cles

| Fonctionnalite | Description |
|---|---|
| **Multi-source** | YouTube, Vimeo, URLs externes, fichiers uploades |
| **Catalogue** | Recherche, filtrage par sujet/categorie/difficulte, pagination |
| **Progression** | Suivi automatique de la position de lecture |
| **Gamification** | +15 XP quand une video est terminee (>= 90%) |
| **Acces controle** | Videos gratuites vs abonnement requis |
| **Administration** | CRUD complet, upload de fichiers, statistiques |
| **Parcours** | Association optionnelle a un parcours d'apprentissage |

---

## 2. Architecture technique

```
┌──────────────┐     ┌─────────────────────────────────────────────┐
│   Frontend    │     │              FastAPI Backend                 │
│              │     │                                              │
│  Lecteur     │────>│  /api/videos/catalog    (catalogue)          │
│  Video       │────>│  /api/videos/{id}       (detail + acces)     │
│  (YouTube /  │────>│  /api/videos/{id}/progress (progression)     │
│   HTML5)     │     │  /api/videos/stream/{f}  (fichier upload)   │
│              │     │  /api/videos/admin/*     (CRUD admin)        │
└──────────────┘     └──────────────┬──────────────────────────────┘
                                    │
                     ┌──────────────▼──────────────┐
                     │        MySQL Database         │
                     │  video_courses (metadonnees)   │
                     │  video_progress (progression)  │
                     └──────────────────────────────┘
                                    │
                     ┌──────────────▼──────────────┐
                     │    Docker Volume              │
                     │    /app/uploads/videos        │
                     │    (fichiers uploades)         │
                     └──────────────────────────────┘
```

### Sources video supportees

| Source | `video_type` | Fonctionnement |
|---|---|---|
| **YouTube** | `youtube` | URL standard → embed automatique |
| **Vimeo** | `vimeo` | URL standard → embed automatique |
| **Upload** | `upload` | Fichier envoye au serveur, servi via `/api/videos/stream/` |
| **Externe** | `external` | URL directe vers un fichier video (CDN, S3, etc.) |

---

## 3. Modeles de donnees

### Table `video_courses`

```sql
CREATE TABLE video_courses (
    id                    VARCHAR(36)  PRIMARY KEY,
    title                 VARCHAR(255) NOT NULL,
    description           TEXT,
    subject               VARCHAR(255) NOT NULL,
    category              VARCHAR(100),
    difficulty            VARCHAR(50)  DEFAULT 'debutant',
    language              VARCHAR(10)  DEFAULT 'fr',
    tags                  TEXT,

    video_url             VARCHAR(500) NOT NULL,
    video_type            VARCHAR(20)  NOT NULL DEFAULT 'youtube',
    thumbnail_url         VARCHAR(500),
    duration_seconds      INT          DEFAULT 0,

    learning_path_id      VARCHAR(36),
    order_index           INT          DEFAULT 0,

    is_free               BOOLEAN      DEFAULT FALSE,
    is_published          BOOLEAN      DEFAULT FALSE,
    requires_subscription BOOLEAN      DEFAULT TRUE,

    views_count           INT          DEFAULT 0,
    likes_count           INT          DEFAULT 0,

    created_by            VARCHAR(36),
    created_at            DATETIME     DEFAULT NOW(),
    updated_at            DATETIME     DEFAULT NOW(),

    INDEX idx_subject (subject),
    INDEX idx_category (category),
    FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id),
    FOREIGN KEY (created_by)       REFERENCES users(id)
);
```

### Table `video_progress`

```sql
CREATE TABLE video_progress (
    id               VARCHAR(36)  PRIMARY KEY,
    user_id          VARCHAR(36)  NOT NULL,
    video_id         VARCHAR(36)  NOT NULL,

    watched_seconds  INT          DEFAULT 0,
    progress_percent FLOAT        DEFAULT 0.0,
    is_completed     BOOLEAN      DEFAULT FALSE,
    watch_count      INT          DEFAULT 1,
    xp_earned        INT          DEFAULT 0,

    last_watched_at  DATETIME     DEFAULT NOW(),
    completed_at     DATETIME,
    created_at       DATETIME     DEFAULT NOW(),

    FOREIGN KEY (user_id)  REFERENCES users(id),
    FOREIGN KEY (video_id) REFERENCES video_courses(id) ON DELETE CASCADE
);
```

---

## 4. Endpoints API - Utilisateurs

> **Prerequis** : Tous les endpoints necessitent un token JWT (`Authorization: Bearer <token>`).

### 4.1 Catalogue de videos

```
GET /api/videos/catalog
```

Catalogue paginee des videos publiees, avec filtrage et recherche.

| Parametre | Type | Defaut | Description |
|---|---|---|---|
| page | int | 1 | Numero de page |
| per_page | int | 12 | Videos par page (max 50) |
| subject | string | - | Filtrer par sujet |
| category | string | - | Filtrer par categorie |
| difficulty | string | - | debutant, intermediaire, avance |
| search | string | - | Recherche dans titre, description, tags |
| is_free | bool | - | Filtrer les videos gratuites |

**Reponse (200 OK) :**

```json
{
    "videos": [
        {
            "id": "abc123...",
            "title": "Introduction a Python - Les bases",
            "subject": "Python",
            "category": "Programmation",
            "difficulty": "debutant",
            "video_type": "youtube",
            "thumbnail_url": "https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg",
            "duration_seconds": 1800,
            "is_free": true,
            "views_count": 245,
            "created_at": "2026-02-11T10:00:00"
        }
    ],
    "total": 42,
    "page": 1,
    "per_page": 12,
    "total_pages": 4
}
```

---

### 4.2 Sujets disponibles

```
GET /api/videos/subjects
```

**Reponse :**

```json
[
    {"subject": "Python", "count": 15},
    {"subject": "Ecologie", "count": 8},
    {"subject": "Intelligence Artificielle", "count": 6}
]
```

---

### 4.3 Categories disponibles

```
GET /api/videos/categories
```

**Reponse :**

```json
[
    {"category": "Programmation", "count": 20},
    {"category": "Sciences", "count": 10},
    {"category": "Environnement", "count": 8}
]
```

---

### 4.4 Detail d'une video

```
GET /api/videos/{video_id}
```

Retourne les details complets de la video, l'URL d'embed, et la progression de l'utilisateur. Verifie l'acces (abonnement) si la video n'est pas gratuite.

**Reponse (200 OK) :**

```json
{
    "video": {
        "id": "abc123...",
        "title": "Introduction a Python - Les bases",
        "description": "Apprenez les fondamentaux de Python...",
        "subject": "Python",
        "category": "Programmation",
        "difficulty": "debutant",
        "language": "fr",
        "tags": "python,programmation,debutant",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "video_type": "youtube",
        "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "duration_seconds": 1800,
        "learning_path_id": null,
        "order_index": 0,
        "is_free": true,
        "is_published": true,
        "requires_subscription": false,
        "views_count": 246,
        "likes_count": 0,
        "created_by": "admin-uuid...",
        "created_at": "2026-02-11T10:00:00",
        "updated_at": "2026-02-11T10:00:00"
    },
    "progress": {
        "id": "prog-uuid...",
        "user_id": "user-uuid...",
        "video_id": "abc123...",
        "watched_seconds": 720,
        "progress_percent": 40.0,
        "is_completed": false,
        "watch_count": 2,
        "xp_earned": 0,
        "last_watched_at": "2026-02-11T18:30:00",
        "completed_at": null
    }
}
```

**Reponse (403 Forbidden) - Sans abonnement :**

```json
{
    "detail": "Abonnement requis pour acceder a cette video. Consultez GET /api/subscriptions/plans pour decouvrir nos offres."
}
```

---

### 4.5 Mettre a jour la progression

```
PUT /api/videos/{video_id}/progress
```

Envoyer regulierement (toutes les 10 secondes) depuis le lecteur video pour sauvegarder la position de lecture.

**Requete :**

```json
{
    "watched_seconds": 720
}
```

**Reponse (200 OK) :**

```json
{
    "id": "prog-uuid...",
    "user_id": "user-uuid...",
    "video_id": "abc123...",
    "watched_seconds": 720,
    "progress_percent": 40.0,
    "is_completed": false,
    "watch_count": 1,
    "xp_earned": 0,
    "last_watched_at": "2026-02-11T18:30:00",
    "completed_at": null
}
```

> **Note** : Quand `progress_percent >= 90%`, la video est automatiquement marquee `is_completed = true` et l'utilisateur recoit **+15 XP**.

---

### 4.6 Recuperer la progression

```
GET /api/videos/{video_id}/progress
```

**Reponse (200 OK) :**

```json
{
    "id": "prog-uuid...",
    "watched_seconds": 720,
    "progress_percent": 40.0,
    "is_completed": false,
    "watch_count": 1
}
```

---

### 4.7 Historique des videos regardees

```
GET /api/videos/me/history
```

Retourne toutes les videos que l'utilisateur a commencees ou terminees, triees par derniere activite.

**Reponse (200 OK) :**

```json
[
    {
        "video": { "id": "...", "title": "Python - Les bases", "..." : "..." },
        "progress": { "watched_seconds": 1620, "progress_percent": 90.0, "is_completed": true }
    },
    {
        "video": { "id": "...", "title": "Ecologie numerique", "..." : "..." },
        "progress": { "watched_seconds": 300, "progress_percent": 25.0, "is_completed": false }
    }
]
```

---

## 5. Endpoints API - Administration

> **Prerequis** : Role `admin` ou `super_admin` requis.

### 5.1 Creer une video (URL)

```
POST /api/videos/admin/create
```

Creer un cours video a partir d'une URL YouTube, Vimeo ou externe.

**Requete :**

```json
{
    "title": "Introduction a Python - Les bases",
    "description": "Apprenez les fondamentaux de Python en 30 minutes",
    "subject": "Python",
    "category": "Programmation",
    "difficulty": "debutant",
    "language": "fr",
    "tags": "python,programmation,debutant,tutorial",
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "video_type": "youtube",
    "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "duration_seconds": 1800,
    "is_free": true,
    "is_published": true,
    "requires_subscription": false
}
```

**Reponse (201 Created) :** VideoCourseResponse complete.

---

### 5.2 Uploader un fichier video

```
POST /api/videos/admin/upload
```

Upload d'un fichier video directement sur le serveur. Utilise un formulaire `multipart/form-data`.

| Parametre | Type | Requis | Description |
|---|---|---|---|
| file | file | Oui | Fichier video (mp4, webm, mkv, avi, mov) - max 500 Mo |
| thumbnail | file | Non | Vignette (jpg, png, webp) |
| title | string (query) | Oui | Titre de la video |
| subject | string (query) | Oui | Sujet |
| description | string (query) | Non | Description |
| category | string (query) | Non | Categorie |
| difficulty | string (query) | Non | Difficulte (defaut: debutant) |
| is_free | bool (query) | Non | Gratuite (defaut: false) |
| is_published | bool (query) | Non | Publiee (defaut: false) |

**Formats autorises :** `.mp4`, `.webm`, `.mkv`, `.avi`, `.mov`
**Taille max :** 500 Mo

---

### 5.3 Modifier une video

```
PUT /api/videos/admin/{video_id}
```

Mettre a jour n'importe quel champ d'une video. Seuls les champs fournis sont mis a jour.

**Requete (exemple partiel) :**

```json
{
    "title": "Python - Les bases (mis a jour)",
    "is_published": true,
    "difficulty": "intermediaire"
}
```

---

### 5.4 Supprimer une video

```
DELETE /api/videos/admin/{video_id}
```

Supprime la video, toutes les progressions associees, et le fichier physique si c'est un upload.

**Reponse :**

```json
{
    "message": "Video 'Python - Les bases' supprimee avec succes.",
    "video_id": "abc123..."
}
```

---

### 5.5 Lister toutes les videos (admin)

```
GET /api/videos/admin/list?include_unpublished=true
```

Liste complete incluant les videos non publiees (brouillons).

---

### 5.6 Statistiques videos

```
GET /api/videos/admin/stats
```

**Reponse :**

```json
{
    "total_videos": 42,
    "published_videos": 35,
    "free_videos": 10,
    "total_views": 12450,
    "total_watch_time_hours": 856.5,
    "completions": 3200,
    "subjects": [
        {"subject": "Python", "count": 15, "views": 5000},
        {"subject": "Ecologie", "count": 8, "views": 3200}
    ]
}
```

---

## 6. Types de videos supportes

### YouTube

```json
{
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "video_type": "youtube",
    "thumbnail_url": "https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg"
}
```

Le backend genere automatiquement l'URL d'embed : `https://www.youtube.com/embed/VIDEO_ID`

URLs supportees :
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

### Vimeo

```json
{
    "video_url": "https://vimeo.com/123456789",
    "video_type": "vimeo"
}
```

Embed genere : `https://player.vimeo.com/video/123456789`

### Upload (fichier local)

```bash
curl -X POST http://206.189.56.166:8000/api/videos/admin/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/chemin/vers/video.mp4" \
  -F "thumbnail=@/chemin/vers/thumbnail.jpg" \
  "title=Mon cours&subject=Python&is_published=true"
```

Le fichier est stocke sur le serveur et servi via : `GET /api/videos/stream/{filename}`

### Externe (CDN, S3, etc.)

```json
{
    "video_url": "https://cdn.example.com/videos/cours-python.mp4",
    "video_type": "external"
}
```

---

## 7. Systeme de progression et XP

### Suivi de progression

Le frontend envoie la position de lecture toutes les **10 secondes** :

```
PUT /api/videos/{video_id}/progress
{"watched_seconds": 720}
```

### Calcul du pourcentage

```
progress_percent = (watched_seconds / duration_seconds) * 100
```

### Completion

| Condition | Action |
|---|---|
| `progress_percent >= 90%` | Video marquee `is_completed = true` |
| Premiere completion | +15 XP attribues a l'utilisateur |
| Re-visionnage | `watch_count` incremente, pas de XP supplementaire |

### Reprise de lecture

La position est sauvegardee automatiquement. Le frontend peut reprendre la lecture via :

```
GET /api/videos/{video_id}/progress → watched_seconds → player.seekTo(watched_seconds)
```

---

## 8. Controle d'acces

| Type de video | Utilisateur sans abonnement | Utilisateur avec abonnement | Admin |
|---|---|---|---|
| `is_free = true` | Acces complet | Acces complet | Acces complet |
| `requires_subscription = true` | 403 Forbidden | Acces complet | Acces complet |
| `is_published = false` | 404 Not Found | 404 Not Found | Acces complet |

---

## 9. Commandes cURL completes

### Prerequis : Token JWT

```bash
TOKEN=$(curl -s -X POST http://206.189.56.166:8000/api/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### 9.1 Admin : Creer une video YouTube

```bash
curl -s -X POST http://206.189.56.166:8000/api/videos/admin/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction a Python - Les bases",
    "description": "Apprenez les fondamentaux de Python : variables, types, conditions, boucles. Cours pour debutants complets.",
    "subject": "Python",
    "category": "Programmation",
    "difficulty": "debutant",
    "tags": "python,programmation,debutant,tutorial",
    "video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
    "video_type": "youtube",
    "thumbnail_url": "https://img.youtube.com/vi/rfscVS0vtbw/maxresdefault.jpg",
    "duration_seconds": 14400,
    "is_free": true,
    "is_published": true,
    "requires_subscription": false
  }' | python3 -m json.tool
```

### 9.2 Admin : Creer une video Vimeo (abonnement requis)

```bash
curl -s -X POST http://206.189.56.166:8000/api/videos/admin/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning avance - Reseaux de neurones",
    "description": "Cours avance sur les reseaux de neurones profonds et le deep learning.",
    "subject": "Intelligence Artificielle",
    "category": "Sciences",
    "difficulty": "avance",
    "tags": "ia,machine-learning,deep-learning,avance",
    "video_url": "https://vimeo.com/123456789",
    "video_type": "vimeo",
    "duration_seconds": 5400,
    "is_free": false,
    "is_published": true,
    "requires_subscription": true
  }' | python3 -m json.tool
```

### 9.3 Admin : Uploader un fichier video

```bash
curl -s -X POST "http://206.189.56.166:8000/api/videos/admin/upload?title=Cours%20Ecologie&subject=Ecologie&difficulty=debutant&is_free=true&is_published=true" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/chemin/vers/ecologie.mp4" \
  -F "thumbnail=@/chemin/vers/thumb.jpg" \
  | python3 -m json.tool
```

### 9.4 Admin : Modifier une video

```bash
curl -s -X PUT http://206.189.56.166:8000/api/videos/admin/VIDEO_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python - Les bases (Edition 2026)",
    "is_published": true,
    "duration_seconds": 1920
  }' | python3 -m json.tool
```

### 9.5 Admin : Supprimer une video

```bash
curl -s -X DELETE http://206.189.56.166:8000/api/videos/admin/VIDEO_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9.6 Admin : Toutes les videos

```bash
curl -s "http://206.189.56.166:8000/api/videos/admin/list?include_unpublished=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9.7 Admin : Statistiques

```bash
curl -s http://206.189.56.166:8000/api/videos/admin/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9.8 Utilisateur : Catalogue

```bash
# Toutes les videos
curl -s "http://206.189.56.166:8000/api/videos/catalog" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Filtrer par sujet
curl -s "http://206.189.56.166:8000/api/videos/catalog?subject=Python&difficulty=debutant" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Rechercher
curl -s "http://206.189.56.166:8000/api/videos/catalog?search=machine+learning" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Videos gratuites seulement
curl -s "http://206.189.56.166:8000/api/videos/catalog?is_free=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9.9 Utilisateur : Voir une video

```bash
curl -s http://206.189.56.166:8000/api/videos/VIDEO_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9.10 Utilisateur : Sauvegarder la progression

```bash
curl -s -X PUT http://206.189.56.166:8000/api/videos/VIDEO_ID/progress \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"watched_seconds": 720}' | python3 -m json.tool
```

### 9.11 Utilisateur : Historique de visionnage

```bash
curl -s http://206.189.56.166:8000/api/videos/me/history \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9.12 Script de test complet

```bash
#!/bin/bash
# ========================================
# Test complet du module Cours Video
# ========================================

BASE_URL="http://206.189.56.166:8000"

echo "=== 1. Login Admin ==="
TOKEN=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:30}..."

echo ""
echo "=== 2. Creer une video YouTube (gratuite) ==="
RESPONSE=$(curl -s -X POST $BASE_URL/api/videos/admin/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python pour debutants",
    "description": "Cours complet Python",
    "subject": "Python",
    "category": "Programmation",
    "difficulty": "debutant",
    "video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
    "video_type": "youtube",
    "duration_seconds": 14400,
    "is_free": true,
    "is_published": true,
    "requires_subscription": false
  }')
echo $RESPONSE | python3 -m json.tool
VIDEO_ID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Video ID: $VIDEO_ID"

echo ""
echo "=== 3. Catalogue ==="
curl -s "$BASE_URL/api/videos/catalog" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 4. Detail de la video ==="
curl -s "$BASE_URL/api/videos/$VIDEO_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 5. Mettre a jour la progression (50%) ==="
curl -s -X PUT "$BASE_URL/api/videos/$VIDEO_ID/progress" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"watched_seconds": 7200}' | python3 -m json.tool

echo ""
echo "=== 6. Mettre a jour la progression (95% -> completion + XP) ==="
curl -s -X PUT "$BASE_URL/api/videos/$VIDEO_ID/progress" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"watched_seconds": 13680}' | python3 -m json.tool

echo ""
echo "=== 7. Historique ==="
curl -s "$BASE_URL/api/videos/me/history" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 8. Statistiques (admin) ==="
curl -s "$BASE_URL/api/videos/admin/stats" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 9. Suppression ==="
curl -s -X DELETE "$BASE_URL/api/videos/admin/$VIDEO_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== Test complet termine ==="
```

---

## 10. Integration Frontend

### 10.1 Service JavaScript

```javascript
const API_BASE = 'http://206.189.56.166:8000';

class VideoService {
    constructor(token) {
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        };
    }

    // Catalogue avec filtres
    async getCatalog({ page = 1, perPage = 12, subject, category, difficulty, search, isFree } = {}) {
        const params = new URLSearchParams({ page, per_page: perPage });
        if (subject) params.append('subject', subject);
        if (category) params.append('category', category);
        if (difficulty) params.append('difficulty', difficulty);
        if (search) params.append('search', search);
        if (isFree !== undefined) params.append('is_free', isFree);

        const res = await fetch(`${API_BASE}/api/videos/catalog?${params}`, { headers: this.headers });
        return res.json();
    }

    // Detail d'une video
    async getVideo(videoId) {
        const res = await fetch(`${API_BASE}/api/videos/${videoId}`, { headers: this.headers });
        if (res.status === 403) throw new Error('SUBSCRIPTION_REQUIRED');
        return res.json();
    }

    // Sauvegarder la progression
    async updateProgress(videoId, watchedSeconds) {
        const res = await fetch(`${API_BASE}/api/videos/${videoId}/progress`, {
            method: 'PUT',
            headers: this.headers,
            body: JSON.stringify({ watched_seconds: watchedSeconds }),
        });
        return res.json();
    }

    // Historique
    async getHistory() {
        const res = await fetch(`${API_BASE}/api/videos/me/history`, { headers: this.headers });
        return res.json();
    }

    // Sujets disponibles
    async getSubjects() {
        const res = await fetch(`${API_BASE}/api/videos/subjects`, { headers: this.headers });
        return res.json();
    }
}
```

### 10.2 Lecteur video avec suivi de progression (React)

```jsx
import React, { useEffect, useRef, useState } from 'react';

function VideoPlayer({ videoId, token }) {
    const videoService = useRef(new VideoService(token));
    const [video, setVideo] = useState(null);
    const [progress, setProgress] = useState(null);
    const playerRef = useRef(null);
    const intervalRef = useRef(null);

    useEffect(() => {
        loadVideo();
        return () => clearInterval(intervalRef.current);
    }, [videoId]);

    async function loadVideo() {
        try {
            const data = await videoService.current.getVideo(videoId);
            setVideo(data.video);
            setProgress(data.progress);
        } catch (err) {
            if (err.message === 'SUBSCRIPTION_REQUIRED') {
                // Afficher modal d'abonnement
            }
        }
    }

    function onPlayerReady() {
        // Reprendre la lecture a la derniere position
        if (progress?.watched_seconds > 0 && playerRef.current) {
            playerRef.current.seekTo(progress.watched_seconds);
        }

        // Sauvegarder la progression toutes les 10 secondes
        intervalRef.current = setInterval(async () => {
            const currentTime = Math.floor(playerRef.current.getCurrentTime());
            const result = await videoService.current.updateProgress(videoId, currentTime);
            setProgress(result);

            if (result.is_completed && result.xp_earned > 0) {
                // Afficher notification "+15 XP !"
            }
        }, 10000);
    }

    if (!video) return <div>Chargement...</div>;

    // Pour YouTube : utiliser react-youtube ou un iframe
    if (video.video_type === 'youtube') {
        const embedUrl = video.video_url.includes('embed/')
            ? video.video_url
            : `https://www.youtube.com/embed/${extractYouTubeId(video.video_url)}`;

        return (
            <div>
                <h2>{video.title}</h2>
                <iframe
                    ref={playerRef}
                    src={embedUrl}
                    width="100%"
                    height="480"
                    frameBorder="0"
                    allowFullScreen
                />
                {progress && (
                    <div className="progress-bar">
                        <div style={{ width: `${progress.progress_percent}%` }} />
                        <span>{progress.progress_percent.toFixed(1)}%</span>
                    </div>
                )}
            </div>
        );
    }

    // Pour upload ou externe : lecteur HTML5
    return (
        <div>
            <h2>{video.title}</h2>
            <video
                ref={playerRef}
                src={video.video_url}
                controls
                width="100%"
                onLoadedData={onPlayerReady}
            />
        </div>
    );
}
```

---

## 11. Gestion des erreurs

| Code | Situation | Message |
|---|---|---|
| **200** | Succes | Reponse avec les donnees |
| **201** | Video creee | VideoCourseResponse |
| **400** | Format fichier invalide / Taille depassee | Detail de l'erreur |
| **401** | Token JWT manquant ou expire | `"Could not validate credentials"` |
| **403** | Abonnement requis | `"Abonnement requis pour acceder a cette video..."` |
| **403** | Non admin | `"Acces reserve aux administrateurs."` |
| **404** | Video introuvable | `"Video introuvable."` |
| **404** | Progression inexistante | `"Aucune progression trouvee pour cette video."` |
| **422** | Validation Pydantic echouee | Details de validation |

---

## Resume des endpoints

| Methode | Endpoint | Acces | Description |
|---|---|---|---|
| GET | `/api/videos/catalog` | Tous | Catalogue pagine avec filtres |
| GET | `/api/videos/subjects` | Tous | Liste des sujets |
| GET | `/api/videos/categories` | Tous | Liste des categories |
| GET | `/api/videos/{id}` | Tous* | Detail + progression |
| PUT | `/api/videos/{id}/progress` | Tous* | Sauvegarder la position |
| GET | `/api/videos/{id}/progress` | Tous | Recuperer la progression |
| GET | `/api/videos/me/history` | Tous | Historique de visionnage |
| POST | `/api/videos/admin/create` | Admin | Creer (URL) |
| POST | `/api/videos/admin/upload` | Admin | Uploader fichier |
| PUT | `/api/videos/admin/{id}` | Admin | Modifier |
| DELETE | `/api/videos/admin/{id}` | Admin | Supprimer |
| GET | `/api/videos/admin/list` | Admin | Lister tout |
| GET | `/api/videos/admin/stats` | Admin | Statistiques |
| GET | `/api/videos/stream/{file}` | Public | Servir fichier uploade |

\* Acces soumis a verification d'abonnement pour les videos non-gratuites.


