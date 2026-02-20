# EcoLearn AI - Documentation Chatbot IA (EcoBot)

**Base URL Production** : `http://206.189.56.166:8000`
**Base URL Locale** : `http://localhost:8000`

---

## Table des matieres

1. [Presentation generale](#1-presentation-generale)
2. [Architecture technique](#2-architecture-technique)
3. [Modele de donnees](#3-modele-de-donnees)
4. [Endpoints API](#4-endpoints-api)
   - [Envoyer un message](#41-envoyer-un-message)
   - [Lister les conversations](#42-lister-les-conversations)
   - [Historique d'une conversation](#43-historique-dune-conversation)
   - [Supprimer une conversation](#44-supprimer-une-conversation)
5. [Schemas Pydantic (Request / Response)](#5-schemas-pydantic)
6. [Service IA Flask (Backend GPT)](#6-service-ia-flask)
7. [Comportement selon abonnement](#7-comportement-selon-abonnement)
8. [Commandes cURL completes](#8-commandes-curl-completes)
9. [Exemples d'integration Frontend](#9-exemples-dintegration-frontend)
10. [Gestion des erreurs](#10-gestion-des-erreurs)
11. [Conformite RGPD](#11-conformite-rgpd)
12. [Diagramme de sequence](#12-diagramme-de-sequence)

---

## 1. Presentation generale

**EcoBot** est le chatbot IA integre a la plateforme EcoLearn AI. Il est propulse par **OpenAI GPT-3.5-turbo** et offre les capacites suivantes :

| Fonctionnalite | Description |
|---|---|
| Questions generales | Repondre a des questions sur tous les sujets (programmation, sciences, langues, etc.) |
| Conseils pedagogiques | Donner des methodes de travail et strategies d'apprentissage |
| Aide plateforme | Expliquer les fonctionnalites de EcoLearn AI |
| Motivation | Encourager et motiver les apprenants |
| Orientation commerciale | Inviter les non-abonnes a decouvrir les offres d'abonnement |

### Regles cles

- **Accessible a TOUS** les utilisateurs authentifies (avec ou sans abonnement)
- **Historique** : les conversations sont sauvegardees en base de donnees
- **Contextuel** : les 10 derniers messages sont envoyes a GPT pour maintenir le contexte
- **Concis** : reponses de 300 mots max
- **RGPD** : l'utilisateur peut supprimer ses conversations a tout moment

---

## 2. Architecture technique

```
┌─────────────┐     ┌──────────────────────┐     ┌──────────────────┐     ┌──────────┐
│   Frontend   │────>│  FastAPI Backend      │────>│  Flask AI Service │────>│  OpenAI  │
│   (Client)   │<────│  /api/chatbot/*       │<────│  /chat            │<────│  GPT-3.5 │
└─────────────┘     └──────────┬───────────┘     └──────────────────┘     └──────────┘
                               │
                     ┌─────────▼─────────┐
                     │   MySQL Database    │
                     │   chat_messages     │
                     └───────────────────┘
```

### Composants

| Composant | Technologie | Role |
|---|---|---|
| **API Gateway** | FastAPI (Python 3.12) | Authentification JWT, validation, persistance des messages, orchestration |
| **Service IA** | Flask (Python) | Construction du prompt systeme, appel OpenAI, gestion du fallback |
| **Modele IA** | OpenAI GPT-3.5-turbo | Generation des reponses conversationnelles |
| **Base de donnees** | MySQL 8.0 | Stockage des messages et historique des conversations |
| **Communication** | HTTP/JSON (httpx async) | FastAPI → Flask via reseau Docker interne |

### Flux de donnees

1. Le **frontend** envoie une requete `POST /api/chatbot/send` avec le message et un token JWT
2. Le **backend FastAPI** :
   - Authentifie l'utilisateur via JWT
   - Verifie le statut d'abonnement
   - Recupere l'historique de la conversation (10 derniers messages)
   - Sauvegarde le message de l'utilisateur en base
   - Appelle le service Flask IA en async
   - Sauvegarde la reponse de l'IA en base
   - Retourne les deux messages au frontend
3. Le **service Flask** :
   - Construit le prompt systeme (contexte utilisateur + regles)
   - Envoie l'historique + message a OpenAI
   - Retourne la reponse (ou un fallback en cas d'erreur)

---

## 3. Modele de donnees

### Table `chat_messages`

```sql
CREATE TABLE chat_messages (
    id              VARCHAR(36)  PRIMARY KEY,    -- UUID v4
    user_id         VARCHAR(36)  NOT NULL,       -- FK → users.id
    conversation_id VARCHAR(36)  NOT NULL,       -- Regroupe les messages d'une conversation
    role            VARCHAR(20)  NOT NULL,       -- "user" ou "assistant"
    content         TEXT         NOT NULL,       -- Contenu du message
    tokens_used     INT          DEFAULT 0,      -- Tokens OpenAI consommes
    created_at      DATETIME     DEFAULT NOW(),  -- Horodatage

    INDEX idx_conversation_id (conversation_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Modele SQLAlchemy

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)       # "user" ou "assistant"
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="chat_messages")
```

### Relation avec User

```python
# Dans models/user.py
class User(Base):
    # ... autres champs ...
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
```

---

## 4. Endpoints API

### 4.1 Envoyer un message

```
POST /api/chatbot/send
```

Envoie un message au chatbot IA. Cree une nouvelle conversation si `conversation_id` est absent, ou continue une conversation existante.

| Parametre | Type | Requis | Description |
|---|---|---|---|
| message | string | Oui | Message de l'utilisateur (1-2000 caracteres) |
| conversation_id | string | Non | UUID d'une conversation existante. Si absent, une nouvelle est creee |

**Authentification** : Bearer Token JWT (requis)
**Abonnement** : Non requis (accessible a tous)

#### Requete

```json
{
    "message": "Bonjour, comment fonctionne le recyclage des dechets electroniques ?",
    "conversation_id": null
}
```

#### Reponse (200 OK)

```json
{
    "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user_message": {
        "id": "11111111-2222-3333-4444-555555555555",
        "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "role": "user",
        "content": "Bonjour, comment fonctionne le recyclage des dechets electroniques ?",
        "tokens_used": 0,
        "created_at": "2026-02-11T18:45:00"
    },
    "assistant_message": {
        "id": "66666666-7777-8888-9999-aaaaaaaaaaaa",
        "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "role": "assistant",
        "content": "Bonjour ! Le recyclage des dechets electroniques (e-waste) est un processus en plusieurs etapes...",
        "tokens_used": 245,
        "created_at": "2026-02-11T18:45:02"
    },
    "has_subscription": false
}
```

---

### 4.2 Lister les conversations

```
GET /api/chatbot/conversations
```

Retourne la liste de toutes les conversations de l'utilisateur connecte, triees par date du dernier message (la plus recente en premier).

**Authentification** : Bearer Token JWT (requis)

#### Reponse (200 OK)

```json
[
    {
        "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "message_count": 6,
        "last_message_at": "2026-02-11T19:30:00",
        "first_message_preview": "Bonjour, comment fonctionne le recyclage des dechets electroniques ?"
    },
    {
        "conversation_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "message_count": 2,
        "last_message_at": "2026-02-11T18:00:00",
        "first_message_preview": "Comment apprendre Python rapidement ?"
    }
]
```

---

### 4.3 Historique d'une conversation

```
GET /api/chatbot/conversations/{conversation_id}
```

Retourne l'historique complet d'une conversation avec tous les messages dans l'ordre chronologique.

| Parametre | Type | Requis | Description |
|---|---|---|---|
| conversation_id | string (path) | Oui | UUID de la conversation |

**Authentification** : Bearer Token JWT (requis)

#### Reponse (200 OK)

```json
{
    "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "messages": [
        {
            "id": "11111111-2222-3333-4444-555555555555",
            "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "role": "user",
            "content": "Bonjour, comment fonctionne le recyclage ?",
            "tokens_used": 0,
            "created_at": "2026-02-11T18:45:00"
        },
        {
            "id": "66666666-7777-8888-9999-aaaaaaaaaaaa",
            "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "role": "assistant",
            "content": "Le recyclage des dechets electroniques...",
            "tokens_used": 245,
            "created_at": "2026-02-11T18:45:02"
        },
        {
            "id": "bbbbbbbb-cccc-dddd-eeee-ffffffffffff",
            "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "role": "user",
            "content": "Et comment reduire mon empreinte carbone ?",
            "tokens_used": 0,
            "created_at": "2026-02-11T18:46:00"
        },
        {
            "id": "gggggggg-hhhh-iiii-jjjj-kkkkkkkkkkkk",
            "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "role": "assistant",
            "content": "Excellente question ! Voici quelques gestes concrets...",
            "tokens_used": 312,
            "created_at": "2026-02-11T18:46:03"
        }
    ],
    "total_messages": 4
}
```

#### Reponse (404 Not Found)

```json
{
    "detail": "Conversation introuvable."
}
```

---

### 4.4 Supprimer une conversation

```
DELETE /api/chatbot/conversations/{conversation_id}
```

Supprime une conversation et **tous ses messages**. Conforme au droit a l'effacement RGPD (Article 17).

| Parametre | Type | Requis | Description |
|---|---|---|---|
| conversation_id | string (path) | Oui | UUID de la conversation a supprimer |

**Authentification** : Bearer Token JWT (requis)

#### Reponse (200 OK)

```json
{
    "message": "Conversation supprimee (6 messages effaces).",
    "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

#### Reponse (404 Not Found)

```json
{
    "detail": "Conversation introuvable."
}
```

---

## 5. Schemas Pydantic

### ChatMessageSend (Requete)

```python
class ChatMessageSend(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
```

| Champ | Type | Contraintes | Description |
|---|---|---|---|
| message | string | 1-2000 caracteres | Message de l'utilisateur |
| conversation_id | string (nullable) | UUID v4 | ID conversation existante ou null |

### ChatMessageResponse (Reponse unitaire)

```python
class ChatMessageResponse(BaseModel):
    id: UUID
    conversation_id: str
    role: str           # "user" ou "assistant"
    content: str
    tokens_used: int
    created_at: datetime
```

### ChatResponse (Reponse complete)

```python
class ChatResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    has_subscription: bool
```

### ConversationSummary (Liste)

```python
class ConversationSummary(BaseModel):
    conversation_id: str
    message_count: int
    last_message_at: datetime
    first_message_preview: str      # 80 premiers caracteres du 1er message
```

### ConversationHistoryResponse (Historique)

```python
class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessageResponse]
    total_messages: int
```

---

## 6. Service IA Flask (Backend GPT)

### Endpoint Flask

```
POST http://ai-service:5000/chat   (reseau Docker interne)
```

### Corps de la requete (envoye par FastAPI)

```json
{
    "message": "Comment apprendre Python ?",
    "conversation_history": [
        {"role": "user", "content": "Bonjour"},
        {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
    ],
    "user_name": "Super Administrateur",
    "has_subscription": true
}
```

### Prompt systeme EcoBot

Le service Flask construit un prompt systeme detaille qui inclut :

```
Tu es EcoBot, l'assistant intelligent de la plateforme EcoLearn AI.
Tu es bienveillant, pedagogique et tu reponds toujours en francais.

A PROPOS DE LA PLATEFORME:
- EcoLearn AI est une plateforme d'apprentissage en ligne intelligente et ecologique
- Elle propose des cours personnalises generes par IA sur differents sujets
- Elle integre un suivi d'empreinte carbone et de la gamification (XP, streaks, badges)
- Les paiements se font par carte bancaire (Visa/MC via Umoja) ou Mobile Money

L'UTILISATEUR:
- Nom : {user_name}
- Abonnement actif : Oui/Non

TES CAPACITES:
- Repondre aux questions generales sur l'apprentissage et l'education
- Expliquer des concepts dans divers domaines
- Donner des conseils d'apprentissage et de methode de travail
- Expliquer les fonctionnalites de la plateforme EcoLearn AI
- Motiver et encourager les apprenants

REGLES:
- Sois concis mais complet (max 300 mots par reponse)
- Si l'utilisateur n'a PAS d'abonnement, rappelle-lui gentiment les avantages
- Ne genere JAMAIS de cours complets (reserve aux abonnes)
- Utilise des emojis avec moderation
```

### Parametres OpenAI

| Parametre | Valeur | Description |
|---|---|---|
| model | gpt-3.5-turbo | Modele utilise |
| max_tokens | 500 | Limite de tokens par reponse |
| temperature | 0.8 | Creativite (0=deterministe, 1=creatif) |
| Contexte | 10 derniers messages | Fenetre de contexte conversationnel |

### Mecanisme de Fallback

Si l'API OpenAI est indisponible, le service retourne une reponse de fallback :

```json
{
    "response": "Bonjour {user_name} ! Je suis EcoBot... Je rencontre un petit probleme technique...",
    "tokens_used": 0,
    "model": "fallback",
    "status": "fallback",
    "error": "Connection timeout"
}
```

---

## 7. Comportement selon abonnement

### Utilisateur AVEC abonnement actif

| Aspect | Comportement |
|---|---|
| Acces chatbot | Complet |
| Reponses | Completes, sans messages commerciaux |
| `has_subscription` | `true` dans la reponse |
| Autres fonctionnalites | Acces aux parcours d'apprentissage + generation IA |

### Utilisateur SANS abonnement

| Aspect | Comportement |
|---|---|
| Acces chatbot | Complet (memes endpoints) |
| Reponses | Completes + rappels occasionnels des avantages de l'abonnement |
| `has_subscription` | `false` dans la reponse |
| Autres fonctionnalites | PAS d'acces a `POST /api/learning/paths` ni `POST /api/learning/sessions` (403) |

### Exemple de reponse IA pour un non-abonne

> "Excellente question ! Le recyclage des dechets electroniques comprend plusieurs etapes...
>
> Pour aller plus loin et suivre un parcours d'apprentissage complet sur l'ecologie numerique, decouvrez nos offres d'abonnement ! Vous aurez acces a des cours generes par IA, des exercices pratiques et un suivi de progression avec gamification."

---

## 8. Commandes cURL completes

### Prerequis : Obtenir un token JWT

```bash
# Login
TOKEN=$(curl -s -X POST http://206.189.56.166:8000/api/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### 8.1 Envoyer un message (nouvelle conversation)

```bash
curl -s -X POST http://206.189.56.166:8000/api/chatbot/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour, comment fonctionne le recyclage des dechets electroniques ?"
  }' | python3 -m json.tool
```

**Reponse attendue :**

```json
{
    "conversation_id": "a1b2c3d4-...",
    "user_message": {
        "id": "...",
        "role": "user",
        "content": "Bonjour, comment fonctionne le recyclage des dechets electroniques ?",
        "tokens_used": 0,
        "created_at": "2026-02-11T18:45:00"
    },
    "assistant_message": {
        "id": "...",
        "role": "assistant",
        "content": "Le recyclage des dechets electroniques...",
        "tokens_used": 245,
        "created_at": "2026-02-11T18:45:02"
    },
    "has_subscription": false
}
```

### 8.2 Continuer une conversation existante

```bash
# Remplacer CONVERSATION_ID par l'id recu dans la reponse precedente
curl -s -X POST http://206.189.56.166:8000/api/chatbot/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Et comment reduire mon empreinte carbone au quotidien ?",
    "conversation_id": "CONVERSATION_ID"
  }' | python3 -m json.tool
```

### 8.3 Lister toutes les conversations

```bash
curl -s http://206.189.56.166:8000/api/chatbot/conversations \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Reponse attendue :**

```json
[
    {
        "conversation_id": "a1b2c3d4-...",
        "message_count": 4,
        "last_message_at": "2026-02-11T19:30:00",
        "first_message_preview": "Bonjour, comment fonctionne le recyclage des dechets electroniques ?"
    }
]
```

### 8.4 Voir l'historique complet d'une conversation

```bash
curl -s http://206.189.56.166:8000/api/chatbot/conversations/CONVERSATION_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 8.5 Supprimer une conversation (RGPD)

```bash
curl -s -X DELETE http://206.189.56.166:8000/api/chatbot/conversations/CONVERSATION_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Reponse attendue :**

```json
{
    "message": "Conversation supprimee (4 messages effaces).",
    "conversation_id": "CONVERSATION_ID"
}
```

### 8.6 Flux complet (script bash)

```bash
#!/bin/bash
# ========================================
# Test complet du chatbot EcoLearn AI
# ========================================

BASE_URL="http://206.189.56.166:8000"

echo "=== 1. Login ==="
TOKEN=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@ecolearnai.com&password=Admin@2026!' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token obtenu: ${TOKEN:0:30}..."

echo ""
echo "=== 2. Premier message (nouvelle conversation) ==="
RESPONSE=$(curl -s -X POST $BASE_URL/api/chatbot/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour ! Quels sont les meilleurs langages de programmation pour debuter ?"}')
echo $RESPONSE | python3 -m json.tool

CONV_ID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['conversation_id'])")
echo "Conversation ID: $CONV_ID"

echo ""
echo "=== 3. Deuxieme message (meme conversation) ==="
curl -s -X POST $BASE_URL/api/chatbot/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Et Python, il est bien pour l'intelligence artificielle ?\", \"conversation_id\": \"$CONV_ID\"}" \
  | python3 -m json.tool

echo ""
echo "=== 4. Troisieme message ==="
curl -s -X POST $BASE_URL/api/chatbot/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Donne-moi un plan d'apprentissage sur 30 jours pour Python\", \"conversation_id\": \"$CONV_ID\"}" \
  | python3 -m json.tool

echo ""
echo "=== 5. Lister les conversations ==="
curl -s $BASE_URL/api/chatbot/conversations \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 6. Historique complet ==="
curl -s $BASE_URL/api/chatbot/conversations/$CONV_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 7. Suppression (RGPD) ==="
curl -s -X DELETE $BASE_URL/api/chatbot/conversations/$CONV_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== Test complet termine ==="
```

---

## 9. Exemples d'integration Frontend

### 9.1 Service JavaScript / TypeScript

```javascript
const API_BASE = 'http://206.189.56.166:8000';

class ChatbotService {
    constructor(token) {
        this.token = token;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        };
    }

    /**
     * Envoyer un message au chatbot.
     * @param {string} message - Le message de l'utilisateur.
     * @param {string|null} conversationId - ID de conversation (null = nouvelle).
     * @returns {Promise<Object>} - La reponse du chatbot.
     */
    async sendMessage(message, conversationId = null) {
        const body = { message };
        if (conversationId) body.conversation_id = conversationId;

        const response = await fetch(`${API_BASE}/api/chatbot/send`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(body),
        });

        if (!response.ok) throw new Error(`Erreur ${response.status}`);
        return response.json();
    }

    /**
     * Lister toutes les conversations.
     * @returns {Promise<Array>} - Liste des conversations.
     */
    async listConversations() {
        const response = await fetch(`${API_BASE}/api/chatbot/conversations`, {
            headers: this.headers,
        });
        if (!response.ok) throw new Error(`Erreur ${response.status}`);
        return response.json();
    }

    /**
     * Recuperer l'historique d'une conversation.
     * @param {string} conversationId - ID de la conversation.
     * @returns {Promise<Object>} - Historique complet.
     */
    async getConversation(conversationId) {
        const response = await fetch(
            `${API_BASE}/api/chatbot/conversations/${conversationId}`,
            { headers: this.headers }
        );
        if (!response.ok) throw new Error(`Erreur ${response.status}`);
        return response.json();
    }

    /**
     * Supprimer une conversation (RGPD).
     * @param {string} conversationId - ID de la conversation.
     * @returns {Promise<Object>} - Confirmation.
     */
    async deleteConversation(conversationId) {
        const response = await fetch(
            `${API_BASE}/api/chatbot/conversations/${conversationId}`,
            { method: 'DELETE', headers: this.headers }
        );
        if (!response.ok) throw new Error(`Erreur ${response.status}`);
        return response.json();
    }
}
```

### 9.2 Exemple d'utilisation dans un composant React

```jsx
import React, { useState, useEffect, useRef } from 'react';

function ChatWidget({ token }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [conversationId, setConversationId] = useState(null);
    const [loading, setLoading] = useState(false);
    const chatbot = useRef(new ChatbotService(token));
    const messagesEndRef = useRef(null);

    // Auto-scroll vers le bas
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setLoading(true);

        // Ajouter le message utilisateur immediatement (optimistic)
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

        try {
            const response = await chatbot.current.sendMessage(userMessage, conversationId);
            setConversationId(response.conversation_id);

            // Ajouter la reponse de l'IA
            setMessages(prev => [
                ...prev,
                {
                    role: 'assistant',
                    content: response.assistant_message.content,
                    tokens: response.assistant_message.tokens_used,
                }
            ]);

            // Afficher une suggestion d'abonnement si non-abonne
            if (!response.has_subscription) {
                // Le frontend peut afficher un bandeau "Abonnez-vous"
            }
        } catch (error) {
            setMessages(prev => [
                ...prev,
                { role: 'assistant', content: 'Erreur de connexion. Reessayez.' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-widget">
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role}`}>
                        <strong>{msg.role === 'user' ? 'Vous' : 'EcoBot'}:</strong>
                        <p>{msg.content}</p>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            <div className="input-area">
                <input
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyPress={e => e.key === 'Enter' && sendMessage()}
                    placeholder="Posez votre question..."
                    disabled={loading}
                />
                <button onClick={sendMessage} disabled={loading}>
                    {loading ? '...' : 'Envoyer'}
                </button>
            </div>
        </div>
    );
}
```

---

## 10. Gestion des erreurs

| Code HTTP | Situation | Message |
|---|---|---|
| **200** | Succes | Reponse avec les messages |
| **400** | Message vide ou > 2000 caracteres | `"value_error"` / `"string_too_long"` |
| **401** | Token JWT manquant ou expire | `"Could not validate credentials"` |
| **404** | Conversation inexistante | `"Conversation introuvable."` |
| **422** | Donnees invalides (validation Pydantic) | Details de validation |
| **500** | Erreur serveur | `"Internal Server Error"` |

### Gestion du timeout OpenAI

Le backend utilise un timeout de **30 secondes** pour l'appel au service Flask :

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(f"{settings.AI_SERVICE_URL}/chat", json={...})
```

Si OpenAI ne repond pas dans les 30 secondes, le fallback est declenche automatiquement.

---

## 11. Conformite RGPD

| Droit RGPD | Implementation |
|---|---|
| **Droit a l'information** (Art. 13) | L'utilisateur sait que ses messages sont stockes (documentation) |
| **Droit d'acces** (Art. 15) | `GET /api/chatbot/conversations` et `GET /api/chatbot/conversations/{id}` |
| **Droit a l'effacement** (Art. 17) | `DELETE /api/chatbot/conversations/{id}` supprime tous les messages |
| **Droit a la portabilite** (Art. 20) | `GET /api/users/data-export` inclut les conversations |
| **Minimisation des donnees** (Art. 5) | Seuls les champs necessaires sont stockes |
| **Limitation de conservation** | Les conversations peuvent etre purgees apres X mois (configurable) |
| **Suppression en cascade** | La suppression du compte utilisateur supprime automatiquement toutes ses conversations (`cascade="all, delete-orphan"`) |

---

## 12. Diagramme de sequence

```
Utilisateur          Frontend             FastAPI Backend           Flask AI Service        OpenAI GPT
    │                    │                       │                        │                      │
    │  Saisit message    │                       │                        │                      │
    │───────────────────>│                       │                        │                      │
    │                    │  POST /api/chatbot/send                        │                      │
    │                    │  {message, conv_id}    │                        │                      │
    │                    │──────────────────────>│                        │                      │
    │                    │                       │                        │                      │
    │                    │                       │  1. Valide JWT         │                      │
    │                    │                       │  2. Verifie abonnement │                      │
    │                    │                       │  3. Charge historique   │                      │
    │                    │                       │     (10 derniers msg)  │                      │
    │                    │                       │  4. Sauve msg user     │                      │
    │                    │                       │     en MySQL           │                      │
    │                    │                       │                        │                      │
    │                    │                       │  POST /chat            │                      │
    │                    │                       │  {message, history,    │                      │
    │                    │                       │   user_name, has_sub}  │                      │
    │                    │                       │──────────────────────>│                      │
    │                    │                       │                        │                      │
    │                    │                       │                        │  Construit prompt     │
    │                    │                       │                        │  systeme + historique  │
    │                    │                       │                        │                      │
    │                    │                       │                        │  chat.completions     │
    │                    │                       │                        │  .create(...)         │
    │                    │                       │                        │─────────────────────>│
    │                    │                       │                        │                      │
    │                    │                       │                        │   Reponse GPT        │
    │                    │                       │                        │<─────────────────────│
    │                    │                       │                        │                      │
    │                    │                       │  {response, tokens}    │                      │
    │                    │                       │<──────────────────────│                      │
    │                    │                       │                        │                      │
    │                    │                       │  5. Sauve reponse IA   │                      │
    │                    │                       │     en MySQL           │                      │
    │                    │                       │  6. Commit transaction │                      │
    │                    │                       │                        │                      │
    │                    │  {conversation_id,     │                        │                      │
    │                    │   user_message,        │                        │                      │
    │                    │   assistant_message,   │                        │                      │
    │                    │   has_subscription}    │                        │                      │
    │                    │<──────────────────────│                        │                      │
    │                    │                       │                        │                      │
    │  Affiche reponse   │                       │                        │                      │
    │<───────────────────│                       │                        │                      │
    │                    │                       │                        │                      │
```

---

## Notes techniques

1. **Timeout** : L'appel au service Flask a un timeout de 30 secondes. Au-dela, le fallback est utilise.
2. **Contexte** : Seuls les 10 derniers messages sont envoyes a GPT pour eviter de depasser la limite de tokens.
3. **Tokens** : Chaque reponse enregistre le nombre de tokens consommes pour le suivi des couts.
4. **Securite** : Un utilisateur ne peut acceder qu'a ses propres conversations (filtre `user_id` sur toutes les requetes).
5. **Preview** : L'apercu dans la liste des conversations est tronque a 80 caracteres.
6. **Cascade** : La suppression d'un utilisateur (`DELETE /api/users/me`) supprime automatiquement toutes ses conversations.
7. **Performance** : L'index sur `conversation_id` optimise les requetes d'historique.
8. **Reseau** : La communication FastAPI ↔ Flask se fait via le reseau Docker interne (`ecolearnai-net`), jamais expose publiquement.

---

