# EcoLearn AI - Modelisation UML & BPMN (Camunda)

**Version** : 1.4.0
**Date** : 11/02/2026

---

## Table des matieres

1. [Diagramme de classes UML](#1-diagramme-de-classes-uml)
2. [Diagramme de cas d'utilisation (Use Case)](#2-diagramme-de-cas-dutilisation)
3. [Diagrammes de sequence UML](#3-diagrammes-de-sequence-uml)
4. [Diagramme d'etats (State Machine)](#4-diagramme-detats)
5. [Diagramme de composants](#5-diagramme-de-composants)
6. [Diagramme de deploiement](#6-diagramme-de-deploiement)
7. [BPMN Camunda - Processus metier](#7-bpmn-camunda---processus-metier)

---

## 1. Diagramme de classes UML

### 1.1 Diagramme complet

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DIAGRAMME DE CLASSES UML                            │
│                        EcoLearn AI v1.4                                 │
└─────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────┐
    │                   «entity»                     │
    │                    User                        │
    ├───────────────────────────────────────────────┤
    │ - id : UUID [PK]                              │
    │ - email : String(255) [UNIQUE, NOT NULL]      │
    │ - phone_number : String(20)                   │
    │ - hashed_password : String(255) [NOT NULL]    │
    │ ─────── Identite ──────                       │
    │ - full_name : String(255) [NOT NULL]          │
    │ - gender : String(20)                         │
    │ ─────── RGPD Chiffre (Fernet AES) ──────     │
    │ - encrypted_date_of_birth : Text              │
    │ - encrypted_nationality : Text                │
    │ - encrypted_national_id : Text                │
    │ - national_id_type : String(50)               │
    │ - encrypted_address_line : Text               │
    │ - encrypted_address_city : Text               │
    │ - encrypted_address_postal_code : Text        │
    │ - encrypted_address_country : Text            │
    │ ─────── Verification ──────                   │
    │ - verification_code : String(10)              │
    │ - verification_code_expires_at : DateTime     │
    │ - is_email_verified : Boolean                 │
    │ ─────── RGPD Consentements ──────             │
    │ - gdpr_consent : Boolean [NOT NULL]           │
    │ - gdpr_consent_at : DateTime                  │
    │ - gdpr_marketing_consent : Boolean            │
    │ - gdpr_data_retention_consent : Boolean       │
    │ ─────── Profil ──────                         │
    │ - avatar_url : String(500)                    │
    │ - bio : Text                                  │
    │ - language : String(10) = "fr"                │
    │ - timezone : String(50) = "Europe/Paris"      │
    │ ─────── Apprentissage ──────                  │
    │ - level : String(50) = "debutant"             │
    │ - objectives : Text                           │
    │ - preferences : Text                          │
    │ ─────── Gamification ──────                   │
    │ - total_xp : Integer = 0                      │
    │ - current_streak : Integer = 0                │
    │ - longest_streak : Integer = 0                │
    │ - last_activity_date : Date                   │
    │ - total_learning_minutes : Float = 0.0        │
    │ ─────── Role & Statut ──────                  │
    │ - role : String(20) = "user"                  │
    │ - is_active : Boolean = true                  │
    │ - is_verified : Boolean = false               │
    │ - last_login_at : DateTime                    │
    │ - deactivated_at : DateTime                   │
    │ ─────── Timestamps ──────                     │
    │ - created_at : DateTime                       │
    │ - updated_at : DateTime                       │
    │ + chat_messages : ChatMessage[*]              │
    ├───────────────────────────────────────────────┤
    │ + register(data) : User                       │
    │ + verifyOTP(code) : Boolean                   │
    │ + login(email, pwd) : Token                   │
    │ + updateProfile(data) : User                  │
    │ + changePassword(old, new) : void             │
    │ + exportData() : UserFullDataExport           │
    │ + deleteAccount() : void                      │
    └──────────┬──┬──┬──┬──┬──┬──┬─────────────────┘
               │  │  │  │  │  │  │
    ┌──────────┘  │  │  │  │  │  └──────────────────────────┐
    │   1..*      │  │  │  │  │                    0..*     │
    │             │  │  │  │  │                             │
    ▼             │  │  │  │  │                             ▼
┌──────────────┐  │  │  │  │  │              ┌──────────────────────┐
│  «entity»    │  │  │  │  │  │              │      «entity»        │
│ Subscription │  │  │  │  │  │              │   UserAchievement    │
├──────────────┤  │  │  │  │  │              ├──────────────────────┤
│- id : UUID   │  │  │  │  │  │              │- id : UUID [PK]     │
│  [PK]        │  │  │  │  │  │              │- user_id : UUID [FK]│
│- user_id :   │  │  │  │  │  │              │- achievement_id :   │
│  UUID [FK]   │  │  │  │  │  │              │  UUID [FK]          │
│- plan :      │  │  │  │  │  │              │- unlocked_at :      │
│  String(50)  │  │  │  │  │  │              │  DateTime           │
│- price :     │  │  │  │  │  │              └───────────┬──────────┘
│  Float       │  │  │  │  │  │                          │ *..1
│- currency :  │  │  │  │  │  │                          │
│  String(10)  │  │  │  │  │  │                          ▼
│- is_active : │  │  │  │  │  │              ┌──────────────────────┐
│  Boolean     │  │  │  │  │  │              │      «entity»        │
│- start_date :│  │  │  │  │  │              │    Achievement       │
│  DateTime    │  │  │  │  │  │              ├──────────────────────┤
│- end_date :  │  │  │  │  │  │              │- id : UUID [PK]     │
│  DateTime    │  │  │  │  │  │              │- code : String(100)  │
│- auto_renew :│  │  │  │  │  │              │  [UNIQUE]            │
│  Boolean     │  │  │  │  │  │              │- name : String(255)  │
│- created_at :│  │  │  │  │  │              │- description : Text  │
│  DateTime    │  │  │  │  │  │              │- icon : String(50)   │
├──────────────┤  │  │  │  │  │              │- category :          │
│+ activate()  │  │  │  │  │  │              │  String(50)          │
│+ deactivate()│  │  │  │  │  │              │- xp_reward : Integer │
│+ isExpired() │  │  │  │  │  │              │- condition_type :    │
└──────┬───────┘  │  │  │  │  │              │  String(100)         │
       │ 1..*     │  │  │  │  │              │- condition_value :   │
       │          │  │  │  │  │              │  Integer             │
       ▼          │  │  │  │  │              │- created_at :        │
┌──────────────┐  │  │  │  │  │              │  DateTime            │
│  «entity»    │  │  │  │  │  │              └──────────────────────┘
│   Payment    │  │  │  │  │  │
├──────────────┤  │  │  │  │  │
│- id : UUID   │  │  │  │  │  │
│  [PK]        │  │  │  │  │  │
│- user_id :   │  │  │  │  │  │
│  UUID [FK]   │  │  │  │  │  │
│- subscript.  │  │  │  │  │  │
│  _id : UUID  │  │  │  │  │  │
│  [FK]        │  │  │  │  │  │
│- amount :    │  │  │  │  │  │
│  Float       │  │  │  │  │  │
│- currency :  │  │  │  │  │  │
│  String(10)  │  │  │  │  │  │
│- payment_    │  │  │  │  │  │
│  method :    │  │  │  │  │  │
│  String(50)  │  │  │  │  │  │
│- status :    │  │  │  │  │  │
│  String(30)  │  │  │  │  │  │
│- transaction │  │  │  │  │  │
│  _ref :      │  │  │  │  │  │
│  String(255) │  │  │  │  │  │
│- invoice_    │  │  │  │  │  │
│  number :    │  │  │  │  │  │
│  String(100) │  │  │  │  │  │
│- invoice_    │  │  │  │  │  │
│  details :   │  │  │  │  │  │
│  Text        │  │  │  │  │  │
│- paid_at :   │  │  │  │  │  │
│  DateTime    │  │  │  │  │  │
│- moko_trans. │  │  │  │  │  │
│  _uuid :     │  │  │  │  │  │
│  String(255) │  │  │  │  │  │
│- moko_pay.   │  │  │  │  │  │
│  _url : Text │  │  │  │  │  │
│- created_at  │  │  │  │  │  │
├──────────────┤  │  │  │  │  │
│+ complete()  │  │  │  │  │  │
│+ fail()      │  │  │  │  │  │
│+ genInvoice()│  │  │  │  │  │
└──────────────┘  │  │  │  │  │
                  │  │  │  │  │
      ┌───────────┘  │  │  │  └───────────┐
      │   1..*       │  │  │    1..*      │
      ▼              │  │  │              ▼
┌──────────────────┐ │  │  │  ┌────────────────────┐
│    «entity»      │ │  │  │  │     «entity»       │
│  LearningPath    │ │  │  │  │  EcoCompensation   │
├──────────────────┤ │  │  │  ├────────────────────┤
│- id : UUID [PK]  │ │  │  │  │- id : UUID [PK]   │
│- user_id : UUID  │ │  │  │  │- user_id : UUID    │
│  [FK]            │ │  │  │  │  [FK]              │
│- title :         │ │  │  │  │- trees_planted :   │
│  String(255)     │ │  │  │  │  Integer           │
│- description :   │ │  │  │  │- co2_compensated   │
│  Text            │ │  │  │  │  _kg : Float       │
│- subject :       │ │  │  │  │- partner_name :    │
│  String(255)     │ │  │  │  │  String(255)       │
│- difficulty :    │ │  │  │  │- partner_reference │
│  String(50)      │ │  │  │  │  : String(255)     │
│- total_sessions :│ │  │  │  │- status :          │
│  Integer         │ │  │  │  │  String(30)        │
│- completed_      │ │  │  │  │- notes : Text      │
│  sessions : Int  │ │  │  │  │- triggered_at :    │
│- progress_       │ │  │  │  │  DateTime          │
│  percent : Float │ │  │  │  │- created_at :      │
│- status :        │ │  │  │  │  DateTime          │
│  String(30)      │ │  │  │  └────────────────────┘
│- created_at      │ │  │  │
│- updated_at      │ │  │  │
├──────────────────┤ │  │  │
│+ complete()      │ │  │  │
│+ getProgress()   │ │  │  │
└──────┬───────────┘ │  │  │
       │ 1..*        │  │  │
       ▼             │  │  │
┌──────────────────┐ │  │  │
│    «entity»      │ │  │  │
│ LearningSession  │ │  │  │
├──────────────────┤ │  │  │
│- id : UUID [PK]  │ │  │  │
│- user_id : UUID  │ │  │  │
│  [FK]            │ │  │  │
│- learning_path   │ │  │  │
│  _id : UUID [FK] │ │  │  │
│- title :         │ │  │  │
│  String(255)     │ │  │  │
│- content : Text  │ │  │  │
│- ai_prompt_used :│ │  │  │
│  Text            │ │  │  │
│- duration_       │ │  │  │
│  minutes : Float │ │  │  │
│- score : Float   │ │  │  │
│- session_number :│ │  │  │
│  Integer         │ │  │  │
│- status :        │ │  │  │
│  String(30)      │ │  │  │
│- started_at      │ │  │  │
│- completed_at    │ │  │  │
│- created_at      │ │  │  │
├──────────────────┤ │  │  │
│+ start()         │ │  │  │
│+ complete(score) │ │  │  │
│+ generateAI()    │ │  │  │
└──────┬───────────┘ │  │  │
       │ 1..1        │  │  │
       ▼             │  │  │
┌──────────────────┐ │  │  │
│    «entity»      │ │  └──┘
│ CarbonFootprint  │ │
├──────────────────┤ │
│- id : UUID [PK]  │ │
│- user_id : UUID  │ │
│  [FK]            │ │
│- session_id :    │ │
│  UUID [FK,UQ]    │ │
│- duration_       │ │
│  minutes : Float │ │
│- energy_kwh :    │ │
│  Float           │ │
│- carbon_kg :     │ │
│  Float           │ │
│- server_region : │ │
│  String(100)     │ │
│- carbon_factor : │ │
│  Float           │ │
│- created_at      │ │
└──────────────────┘ │
                     │
              ┌──────┘
              │
              ▼
┌──────────────────────┐
│      «entity»        │
│  SubscriptionPlan    │
├──────────────────────┤
│- id : UUID [PK]     │
│- code : String(50)   │
│  [UNIQUE]            │
│- name : String(255)  │
│- description : Text  │
│- price : Float       │
│- currency :          │
│  String(10) = "USD"  │
│- duration_days :     │
│  Integer             │
│- is_active :         │
│  Boolean = true      │
│- features : Text     │
│- max_sessions_       │
│  per_day : Integer   │
│- sort_order :        │
│  Integer = 0         │
│- created_at          │
│- updated_at          │
├──────────────────────┤
│+ activate()          │
│+ deactivate()        │
│+ updatePrice(price)  │
└──────────────────────┘

    ┌───────────────────────────────────────────────┐
    │                   «entity»                     │
    │                 ChatMessage                    │
    ├───────────────────────────────────────────────┤
    │ - id : UUID [PK]                              │
    │ - user_id : UUID [FK → User]                  │
    │ - conversation_id : UUID [INDEX]              │
    │ - role : String(20) [NOT NULL]                │
    │   {user, assistant}                           │
    │ - content : Text [NOT NULL]                   │
    │ - tokens_used : Integer = 0                   │
    │ - created_at : DateTime                       │
    ├───────────────────────────────────────────────┤
    │ + getConversationHistory() : List<ChatMessage>│
    └───────────────────────────────────────────────┘
```

### 1.2 Relations entre entites

```
┌──────────────────────────────────────────────────────────────────┐
│                     RELATIONS (CARDINALITES)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User ──────< Subscription        1 User   → 0..* Subscriptions │
│  User ──────< Payment             1 User   → 0..* Payments      │
│  User ──────< LearningPath        1 User   → 0..* LearningPaths │
│  User ──────< LearningSession     1 User   → 0..* Sessions      │
│  User ──────< CarbonFootprint     1 User   → 0..* Footprints    │
│  User ──────< EcoCompensation     1 User   → 0..* Compensations │
│  User ──────< UserAchievement     1 User   → 0..* Badges        │
│  User ──────< ChatMessage         1 User   → 0..* ChatMessages  │
│                                                                  │
│  Subscription ────< Payment       1 Sub    → 1..* Payments      │
│  LearningPath ────< LearningSession                             │
│                                   1 Path   → 0..* Sessions      │
│  LearningSession ──── CarbonFootprint                            │
│                                   1 Session→ 0..1 Footprint     │
│  Achievement ────< UserAchievement                               │
│                                   1 Badge  → 0..* UserBadges    │
│                                                                  │
│  SubscriptionPlan (catalogue, pas de FK directe)                 │
│    → lie a Subscription par Subscription.plan = Plan.code        │
│                                                                  │
│  Notation : ──────<  = One-to-Many (cascade delete)              │
│             ──────   = One-to-One                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagramme de cas d'utilisation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  DIAGRAMME DE CAS D'UTILISATION                         │
└─────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────────────────────┐
                         │          SYSTEME ECOLEARNAI          │
                         │                                     │
  ┌─────────┐            │  ┌─────────────────────────────┐   │
  │         │            │  │   UC1: S'inscrire            │   │
  │ Visiteur├───────────►│  │   (email+tel+RGPD)          │   │
  │         │            │  └──────────────┬──────────────┘   │
  └─────────┘            │                 │ «include»        │
                         │  ┌──────────────▼──────────────┐   │
                         │  │   UC2: Verifier OTP          │   │
                         │  │   (SMS + Email)              │   │
  ┌─────────┐            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │   UC3: Se connecter          │   │
  │         │            │  │   (JWT Token)                │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │   UC4: Gerer son profil      │   │
  │         │            │  │   (modifier, mot de passe)   │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │ Utilisa-├───────────►│  │   UC5: S'abonner             │   │
  │  teur   │            │  │   (choisir plan + payer)     │   │
  │         │            │  └──────────────┬──────────────┘   │
  │         │            │     «extend»    │    «extend»      │
  │         │            │  ┌──────────────┘──────────┐       │
  │         │            │  │                         │       │
  │         │            │  ▼                         ▼       │
  │         │            │  ┌──────────────┐ ┌────────────┐   │
  │         │            │  │UC5a: Payer   │ │UC5b: Payer │   │
  │         │            │  │Mobile Money  │ │Carte Visa  │   │  ──► Umoja API
  │         │            │  └──────────────┘ └────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │   UC6: Creer parcours        │   │
  │         │            │  │   d'apprentissage            │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │   UC7: Suivre une session    │   │  ──► OpenAI GPT
  │         │            │  │   (contenu genere par IA)    │   │
  │         │            │  └──────────────┬──────────────┘   │
  │         │            │                 │ «include»        │
  │         │            │  ┌──────────────▼──────────────┐   │
  │         │            │  │   UC8: Terminer session      │   │
  │         │            │  │   (score, XP, streak,        │   │
  │         │            │  │    carbone, badges)           │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │   UC9: Consulter dashboard    │   │
  │         │            │  │   (stats, carbone, badges)   │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │  UC10: Exercer droits RGPD   │   │
  │         │            │  │  (export, suppression,        │   │
  │         │            │  │   consentement)               │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │  (Discuter avec le chatbot IA)   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │  (Lister ses conversations)     │
  │         │            │  └─────────────────────────────┘   │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │  (Supprimer une conversation [RGPD]) │
  │         │            │  └─────────────────────────────┘   │
  └─────────┘            │                                     │
                         │                                     │
  ┌─────────┐            │  ┌─────────────────────────────┐   │
  │         │            │  │  UC11: Gerer les plans       │   │
  │  Admin  ├───────────►│  │  (CRUD abonnements)         │   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │  UC12: Gerer utilisateurs    │   │
  │         │            │  │  (activer, desactiver, roles)│   │
  │         │            │  └─────────────────────────────┘   │
  │         │            │                                     │
  │         │            │  ┌─────────────────────────────┐   │
  │         ├───────────►│  │  UC13: Voir dashboard admin  │   │
  │         │            │  │  (KPIs, revenus, stats)      │   │
  └─────────┘            │  └─────────────────────────────┘   │
                         │                                     │
                         │                                     │
  ┌─────────┐            │  ┌─────────────────────────────┐   │
  │ Super   │            │  │  UC14: Gerer les roles       │   │
  │ Admin   ├───────────►│  │  (promouvoir admin)          │   │
  │         │            │  └─────────────────────────────┘   │
  └─────────┘            │                                     │
                         │                                     │
  ┌─────────┐            │  ┌─────────────────────────────┐   │
  │ Umoja   │            │  │  UC15: Notifier paiement     │   │
  │ CardAPI ├───────────►│  │  (callback webhook)          │   │
  │(systeme)│            │  └─────────────────────────────┘   │
  └─────────┘            │                                     │
                         └─────────────────────────────────────┘
```

---

## 3. Diagrammes de sequence UML

### 3.1 Inscription et verification

```
┌──────┐     ┌──────────┐     ┌───────┐     ┌───────┐     ┌──────┐   ┌──────┐
│Client│     │ Frontend │     │Backend│     │ MySQL │     │MGT-SM│   │Gmail │
│      │     │          │     │FastAPI│     │       │     │  S   │   │ SMTP │
└──┬───┘     └────┬─────┘     └───┬───┘     └───┬───┘     └──┬───┘   └──┬───┘
   │              │               │             │            │          │
   │ 1. Formulaire│               │             │            │          │
   │  inscription │               │             │            │          │
   │─────────────>│               │             │            │          │
   │              │               │             │            │          │
   │              │ 2. POST       │             │            │          │
   │              │ /api/auth/    │             │            │          │
   │              │ register      │             │            │          │
   │              │──────────────>│             │            │          │
   │              │               │             │            │          │
   │              │               │ 3. Verifier │            │          │
   │              │               │ email unique│            │          │
   │              │               │────────────>│            │          │
   │              │               │<────────────│            │          │
   │              │               │             │            │          │
   │              │               │ 4. Verifier │            │          │
   │              │               │ tel unique  │            │          │
   │              │               │────────────>│            │          │
   │              │               │<────────────│            │          │
   │              │               │             │            │          │
   │              │               │ 5. Generer  │            │          │
   │              │               │ OTP code    │            │          │
   │              │               │─────┐       │            │          │
   │              │               │     │       │            │          │
   │              │               │<────┘       │            │          │
   │              │               │             │            │          │
   │              │               │ 6. Chiffrer │            │          │
   │              │               │ donnees RGPD│            │          │
   │              │               │ (Fernet AES)│            │          │
   │              │               │─────┐       │            │          │
   │              │               │<────┘       │            │          │
   │              │               │             │            │          │
   │              │               │ 7. INSERT   │            │          │
   │              │               │ User        │            │          │
   │              │               │────────────>│            │          │
   │              │               │<────────────│            │          │
   │              │               │             │            │          │
   │              │               │ 8. Envoyer SMS──────────>│          │
   │              │               │             │            │          │
   │              │               │ 9. Envoyer Email────────────────────>│
   │              │               │             │            │          │
   │              │ 10. 201       │             │            │          │
   │              │ {sms_sent,    │             │            │          │
   │              │  email_sent}  │             │            │          │
   │              │<──────────────│             │            │          │
   │              │               │             │            │          │
   │ 11. Afficher │               │             │            │          │
   │ "Code envoye"│               │             │            │          │
   │<─────────────│               │             │            │          │
   │              │               │             │            │          │
   │ 12. Saisir   │               │             │            │          │
   │ code OTP     │               │             │            │          │
   │─────────────>│               │             │            │          │
   │              │               │             │            │          │
   │              │ 13. POST      │             │            │          │
   │              │ /api/auth/    │             │            │          │
   │              │ verify-sms    │             │            │          │
   │              │──────────────>│             │            │          │
   │              │               │             │            │          │
   │              │               │ 14. Verifier│            │          │
   │              │               │ code + expir│            │          │
   │              │               │────────────>│            │          │
   │              │               │<────────────│            │          │
   │              │               │             │            │          │
   │              │               │ 15. UPDATE  │            │          │
   │              │               │ is_verified │            │          │
   │              │               │ = true      │            │          │
   │              │               │────────────>│            │          │
   │              │               │             │            │          │
   │              │ 16. 200 OK    │             │            │          │
   │              │ "Compte       │             │            │          │
   │              │  verifie"     │             │            │          │
   │              │<──────────────│             │            │          │
   │              │               │             │            │          │
   │ 17. Redirect │               │             │            │          │
   │ vers login   │               │             │            │          │
   │<─────────────│               │             │            │          │
```

### 3.2 Paiement carte bancaire (Visa/MC via Umoja)

```
┌──────┐   ┌────────┐   ┌───────┐   ┌─────┐   ┌──────┐   ┌─────┐  ┌─────┐
│Client│   │Frontend│   │Backend│   │MySQL│   │Umoja │   │ SMS │  │Email│
└──┬───┘   └───┬────┘   └───┬───┘   └──┬──┘   │CardAP│   │ API │  │SMTP │
   │           │             │          │      └──┬───┘   └──┬──┘  └──┬──┘
   │ 1. Clic   │             │          │         │          │        │
   │ "S'abonner│             │          │         │          │        │
   │  annuel"  │             │          │         │          │        │
   │──────────>│             │          │         │          │        │
   │           │             │          │         │          │        │
   │           │ 2. POST /api│          │         │          │        │
   │           │ /subscribe  │          │         │          │        │
   │           │ {plan:annuel│          │         │          │        │
   │           │  method:    │          │         │          │        │
   │           │  carte}     │          │         │          │        │
   │           │────────────>│          │         │          │        │
   │           │             │          │         │          │        │
   │           │             │ 3.INSERT │         │          │        │
   │           │             │ Subscript│         │          │        │
   │           │             │ (pending)│         │          │        │
   │           │             │─────────>│         │          │        │
   │           │             │          │         │          │        │
   │           │             │ 4.INSERT │         │          │        │
   │           │             │ Payment  │         │          │        │
   │           │             │ (pending)│         │          │        │
   │           │             │─────────>│         │          │        │
   │           │             │          │         │          │        │
   │           │             │ 5. POST /api/v1/   │          │        │
   │           │             │ payment/orders     │          │        │
   │           │             │ (HMAC-SHA256)      │          │        │
   │           │             │───────────────────>│          │        │
   │           │             │                    │          │        │
   │           │             │ 6. {payment_url,   │          │        │
   │           │             │  transaction_uuid} │          │        │
   │           │             │<───────────────────│          │        │
   │           │             │          │         │          │        │
   │           │             │ 7.UPDATE │         │          │        │
   │           │             │ moko_uuid│         │          │        │
   │           │             │─────────>│         │          │        │
   │           │             │          │         │          │        │
   │           │ 8. Redirect │          │         │          │        │
   │           │ payment_url │          │         │          │        │
   │           │<────────────│          │         │          │        │
   │           │             │          │         │          │        │
   │ 9. Redirect             │          │         │          │        │
   │ page Moko│              │          │         │          │        │
   │<──────────│             │          │         │          │        │
   │           │             │          │         │          │        │
   │═══════════╪═════════════╪══════════╪═════════│══════════╪════════╪══
   │ 10. SAISIE CARTE BANCAIRE         │         │          │        │
   │ (Page securisee Umoja)             │         │          │        │
   │═══════════════════════════════════>│         │          │        │
   │                         │          │         │          │        │
   │ 11. Redirect retour site│          │         │          │        │
   │<══════════════════════════════════│          │          │        │
   │           │             │          │         │          │        │
   │──────────>│             │          │         │          │        │
   │           │ 12. GET     │          │         │          │        │
   │           │ /payment/   │          │         │          │        │
   │           │ {id}/status │          │         │          │        │
   │           │────────────>│          │         │          │        │
   │           │ "pending"   │          │         │          │        │
   │           │<────────────│          │         │          │        │
   │           │  (polling)  │          │         │          │        │
   │           │             │          │         │          │        │
   │           │             │ 13. POST │         │          │        │
   │           │             │ /callback│ (HMAC)  │          │        │
   │           │             │<───────────────────│          │        │
   │           │             │          │         │          │        │
   │           │             │14.Verify │         │          │        │
   │           │             │ HMAC sig │         │          │        │
   │           │             │──┐       │         │          │        │
   │           │             │<─┘       │         │          │        │
   │           │             │          │         │          │        │
   │           │             │15.UPDATE │         │          │        │
   │           │             │ Payment  │         │          │        │
   │           │             │=completed│         │          │        │
   │           │             │─────────>│         │          │        │
   │           │             │          │         │          │        │
   │           │             │16.UPDATE │         │          │        │
   │           │             │ Subscript│         │          │        │
   │           │             │=active   │         │          │        │
   │           │             │─────────>│         │          │        │
   │           │             │          │         │          │        │
   │           │             │ 17. SMS confirmation────────>│        │
   │           │             │ 18. Email confirmation────────────────>│
   │           │             │          │         │          │        │
   │           │ 19. GET     │          │         │          │        │
   │           │ /status     │          │         │          │        │
   │           │────────────>│          │         │          │        │
   │           │ "completed" │          │         │          │        │
   │           │<────────────│          │         │          │        │
   │           │             │          │         │          │        │
   │ 20. "Abonnement actif!" │          │         │          │        │
   │<──────────│             │          │         │          │        │
```

### 3.3 Session d'apprentissage (IA)

```
┌──────┐   ┌────────┐   ┌───────┐   ┌─────┐   ┌──────┐   ┌───────┐
│Client│   │Frontend│   │Backend│   │MySQL│   │Flask │   │OpenAI │
│      │   │        │   │FastAPI│   │     │   │AI Svc│   │GPT API│
└──┬───┘   └───┬────┘   └───┬───┘   └──┬──┘   └──┬───┘   └───┬───┘
   │           │             │          │         │            │
   │ 1."Demarrer             │          │         │            │
   │  session" │             │          │         │            │
   │──────────>│             │          │         │            │
   │           │ 2. POST     │          │         │            │
   │           │ /sessions   │          │         │            │
   │           │────────────>│          │         │            │
   │           │             │          │         │            │
   │           │             │ 3.SELECT │         │            │
   │           │             │ path     │         │            │
   │           │             │─────────>│         │            │
   │           │             │<─────────│         │            │
   │           │             │          │         │            │
   │           │             │ 4. POST /generate  │            │
   │           │             │ {subject, level,   │            │
   │           │             │  session_number}   │            │
   │           │             │───────────────────>│            │
   │           │             │          │         │            │
   │           │             │          │         │ 5. POST    │
   │           │             │          │         │ /chat/     │
   │           │             │          │         │completions │
   │           │             │          │         │───────────>│
   │           │             │          │         │            │
   │           │             │          │         │ 6. Contenu │
   │           │             │          │         │ pedagogique│
   │           │             │          │         │<───────────│
   │           │             │          │         │            │
   │           │             │ 7. {content,       │            │
   │           │             │  prompt_used}      │            │
   │           │             │<───────────────────│            │
   │           │             │          │         │            │
   │           │             │ 8.INSERT │         │            │
   │           │             │ Session  │         │            │
   │           │             │─────────>│         │            │
   │           │             │          │         │            │
   │           │ 9. Session  │          │         │            │
   │           │ + contenu IA│          │         │            │
   │           │<────────────│          │         │            │
   │           │             │          │         │            │
   │ 10. Lecon │             │          │         │            │
   │ affichee  │             │          │         │            │
   │<──────────│             │          │         │            │
   │           │             │          │         │            │
   │ ... etude ...           │          │         │            │
   │           │             │          │         │            │
   │ 11. Terminer            │          │         │            │
   │ score=85  │             │          │         │            │
   │──────────>│             │          │         │            │
   │           │ 12. PUT     │          │         │            │
   │           │ /sessions/  │          │         │            │
   │           │ {id}/       │          │         │            │
   │           │ complete    │          │         │            │
   │           │────────────>│          │         │            │
   │           │             │          │         │            │
   │           │             │ 13. Calculs en chaine :        │
   │           │             │ ┌────────────────────────────┐ │
   │           │             │ │ a) Mettre a jour session   │ │
   │           │             │ │ b) Calculer empreinte CO2  │ │
   │           │             │ │ c) Attribuer XP (+score)   │ │
   │           │             │ │ d) Mettre a jour streak    │ │
   │           │             │ │ e) Cumuler temps           │ │
   │           │             │ │ f) Mettre a jour parcours  │ │
   │           │             │ │ g) Verifier montee niveau  │ │
   │           │             │ │ h) Verifier badges         │ │
   │           │             │ │ i) Verifier compensation   │ │
   │           │             │ │    ecologique               │ │
   │           │             │ └────────────────────────────┘ │
   │           │             │          │         │            │
   │           │             │ 14. COMMIT│        │            │
   │           │             │ (toutes   │        │            │
   │           │             │ les MAJ)  │        │            │
   │           │             │─────────>│         │            │
   │           │             │          │         │            │
   │           │ 15. Reponse │          │         │            │
   │           │ {xp, streak,│          │         │            │
   │           │  badges,    │          │         │            │
   │           │  carbon,    │          │         │            │
   │           │  level_up}  │          │         │            │
   │           │<────────────│          │         │            │
   │           │             │          │         │            │
   │ 16."Bravo!│             │          │         │            │
   │  +50 XP"  │             │          │         │            │
   │<──────────│             │          │         │            │
```

---

## 4. Diagramme d'etats

### 4.1 Etats du compte utilisateur

```
                    ┌───────────┐
                    │   START   │
                    └─────┬─────┘
                          │ register()
                          ▼
                 ┌─────────────────┐
                 │   NON_VERIFIE   │
                 │  (is_verified   │
                 │   = false)      │
                 └────────┬────────┘
                          │ verifyOTP()
                          ▼
                 ┌─────────────────┐
             ┌──>│     ACTIF       │<──┐
             │   │  (is_verified   │   │
             │   │   = true,       │   │
             │   │   is_active     │   │
             │   │   = true)       │   │
             │   └───┬─────────┬───┘   │
             │       │         │       │
             │admin  │         │admin  │
             │activ. │deactiv. │delete │
             │       ▼         │       │
             │  ┌──────────┐   │       │
             └──│ DESACTIVE│   │       │
                │(is_active│   │       │
                │ = false) │   │       │
                └──────────┘   │       │
                               ▼       │
                          ┌────────┐   │
                          │SUPPRIME│   │
                          │(DELETE │   │
                          │ cascade)│   │
                          └────────┘   │
                                       │
                    reactiver()────────┘
```

### 4.2 Etats du paiement

```
         ┌───────────┐
         │   START   │
         └─────┬─────┘
               │ create_subscription_pending()
               ▼
      ┌─────────────────┐
      │     PENDING     │
      │ (en attente du  │
      │  paiement carte)│
      └───┬─────────┬───┘
          │         │
  callback│   callback
  success │   failed
          │         │
          ▼         ▼
  ┌──────────┐  ┌──────────┐
  │COMPLETED │  │  FAILED  │
  │(paiement │  │(paiement │
  │ reussi,  │  │ echoue)  │
  │ abonnmt  │  │          │
  │ actif)   │  │          │
  └──────────┘  └──────────┘
      │              │
      │              │
      ▼              ▼
  SMS + Email    SMS + Email
  confirmation   echec
```

### 4.3 Etats de l'abonnement

```
       ┌───────────┐
       │   START   │
       └─────┬─────┘
             │ subscribe()
             ▼
    ┌─────────────────┐     callback success
    │    INACTIF      │─────────────────────┐
    │ (en attente     │                     │
    │  paiement carte)│                     │
    └─────────────────┘                     │
             │                              │
             │ mobile_money (immediat)      │
             │                              │
             ▼                              ▼
    ┌─────────────────┐            ┌──────────────┐
    │     ACTIF       │<───────────│    ACTIF     │
    │ (abonnement     │            │   (active    │
    │  en cours)      │            │    par       │
    │                 │            │   callback)  │
    └────────┬────────┘            └──────────────┘
             │
             │ end_date atteinte
             ▼
    ┌─────────────────┐
    │     EXPIRE      │
    │ (auto_renew?    │
    │  -> renouveler) │
    └─────────────────┘
```

### 4.4 Etats de la session d'apprentissage

```
       ┌───────────┐
       │   START   │
       └─────┬─────┘
             │ start_session()
             ▼
    ┌─────────────────┐
    │    EN_COURS     │
    │ (contenu IA     │
    │  genere)        │
    └───┬─────────┬───┘
        │         │
complete│   abandon│
(score) │         │
        ▼         ▼
  ┌──────────┐  ┌──────────┐
  │ TERMINEE │  │ABANDONNEE│
  │          │  │          │
  │ Triggers:│  └──────────┘
  │ - XP     │
  │ - Streak │
  │ - Carbon │
  │ - Badges │
  │ - Level  │
  └──────────┘
```

---

## 5. Diagramme de composants

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DIAGRAMME DE COMPOSANTS                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     «application»                                │
│                     FastAPI Backend                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    «component»                            │   │
│  │                     Routers                               │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │   │
│  │  │ auth │ │users │ │subscr│ │pay-  │ │learn-│ │carbon│ │   │
│  │  │      │ │      │ │iption│ │ments │ │ing   │ │      │ │   │
│  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ │   │
│  │  ┌──┴───┐ ┌──┴───┐ ┌──┴─────┐                          │   │
│  │  │dash- │ │admin │ │monitor-│                            │   │
│  │  │board │ │      │ │ing     │                            │   │
│  │  └──────┘ └──────┘ └────────┘                            │   │
│  └──────────────────────────────┬───────────────────────────┘   │
│                                 │ depends                        │
│  ┌──────────────────────────────▼───────────────────────────┐   │
│  │                    «component»                            │   │
│  │                     Services                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │ Payment  │ │Progression│ │  Carbon  │ │  Moko    │    │   │
│  │  │ Service  │ │  Service │ │  Service │ │  Service │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │   SMS    │ │  Email   │ │Encryption│ │  Cache   │    │   │
│  │  │ Service  │ │  Service │ │  Service │ │ (Redis)  │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  │  ┌──────────┐ ┌──────────────┐                           │   │
│  │  │  Backup  │ │ APScheduler  │                           │   │
│  │  │ Service  │ │ (Cron 01:00) │                           │   │
│  │  └──────────┘ └──────────────┘                           │   │
│  └──────────────────────────────┬───────────────────────────┘   │
│                                 │ depends                        │
│  ┌──────────────────────────────▼───────────────────────────┐   │
│  │                    «component»                            │   │
│  │                   Models (ORM)                             │   │
│  │  User | Subscription | Payment | SubscriptionPlan         │   │
│  │  LearningPath | LearningSession | CarbonFootprint         │   │
│  │  EcoCompensation | Achievement | UserAchievement          │   │
│  └──────────────────────────────┬───────────────────────────┘   │
│                                 │ SQLAlchemy                     │
│  ┌──────────────────────────────▼───────────────────────────┐   │
│  │                    «component»                            │   │
│  │                Security & Utils                            │   │
│  │  JWT Auth | Password Hash | RBAC | Fernet Encryption      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │              │              │              │
         │ HTTP         │ HTTP         │ SMTP         │ HTTP
         ▼              ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ «extern» │  │ «extern» │  │ «extern» │  │ «extern» │
  │  Umoja   │  │ MGT-SMS  │  │  Gmail   │  │ OpenAI   │
  │ CardAPI  │  │   API    │  │  SMTP    │  │ GPT API  │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 6. Diagramme de deploiement

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DIAGRAMME DE DEPLOIEMENT                            │
└─────────────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────────┐
  │              «device» Poste Client                            │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
  │  │ «artifact»  │  │ «artifact»  │  │ «artifact»  │          │
  │  │ Chrome      │  │ Safari      │  │ Mobile App  │          │
  │  │ (SPA React) │  │ (SPA React) │  │ (RN)        │          │
  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
  └─────────┼────────────────┼────────────────┼──────────────────┘
            │ HTTPS          │ HTTPS          │ HTTPS
            └────────────────┼────────────────┘
                             │
  ┌──────────────────────────▼────────────────────────────────────┐
  │     «execution environment» Serveur Production                │
  │     IP: 206.189.56.166 (DigitalOcean Droplet)                │
  │                                                               │
  │  ┌─────────────────────────────────────────────────────┐     │
  │  │         «container» Docker Compose                   │     │
  │  │                                                      │     │
  │  │  ┌──────────────────────┐  ┌──────────────────────┐ │     │
  │  │  │  «container»         │  │  «container»         │ │     │
  │  │  │  ecolearnai-backend  │  │  ecolearnai-ai       │ │     │
  │  │  │  ────────────────    │  │  ────────────────    │ │     │
  │  │  │  FastAPI + Uvicorn   │  │  Flask + Gunicorn    │ │     │
  │  │  │  Python 3.12         │  │  Python 3.12         │ │     │
  │  │  │  Port: 8000          │  │  Port: 5000          │ │     │
  │  │  │                      │  │                      │ │     │
  │  │  │  «artifact»          │  │  «artifact»          │ │     │
  │  │  │  - main.py           │  │  - app.py            │ │     │
  │  │  │  - routers/*.py      │  │  - OpenAI client     │ │     │
  │  │  │  - services/*.py     │  │                      │ │     │
  │  │  │  - models/*.py       │  │                      │ │     │
  │  │  │  - schemas/*.py      │  │                      │ │     │
  │  │  │  - utils/*.py        │  │                      │ │     │
  │  │  │  + cache_service.py  │  │                      │ │     │
  │  │  │  + backup_service.py │  │                      │ │     │
  │  │  │  + APScheduler cron  │  │                      │ │     │
  │  │  └──────────┬───────────┘  └──────────────────────┘ │     │
  │  │             │                                        │     │
  │  │  ┌──────────┴───────────┐  ┌──────────────────────┐ │     │
  │  │  │  «container»         │  │  «container»         │ │     │
  │  │  │  ecolearnai-redis    │  │  ecolearnai-prom.    │ │     │
  │  │  │  ────────────────    │  │  ────────────────    │ │     │
  │  │  │  Redis 7.2 Alpine    │  │  Prometheus v2.51   │ │     │
  │  │  │  256 Mo, LRU, AOF   │  │  Retention: 30j     │ │     │
  │  │  │  Port: 6379          │  │  Port: 9090         │ │     │
  │  │  └──────────────────────┘  └──────────────────────┘ │     │
  │  │                                                      │     │
  │  │  ┌──────────────────────┐  ┌──────────────────────┐ │     │
  │  │  │  «container»         │  │  «container»         │ │     │
  │  │  │  ecolearnai-grafana  │  │  node/redis/mysql    │ │     │
  │  │  │  ────────────────    │  │  exporters           │ │     │
  │  │  │  Grafana 10.4        │  │  ────────────────    │ │     │
  │  │  │  Dashboard auto      │  │  :9100, :9121, :9104 │ │     │
  │  │  │  Port: 3000          │  │  Metriques OS/DB/Cach│ │     │
  │  │  └──────────────────────┘  └──────────────────────┘ │     │
  │  │                                                      │     │
  │  └──────────────────────────────────────────────────────┘     │
  │                │ PyMySQL (TCP 3306)                            │
  └────────────────┼──────────────────────────────────────────────┘
                   │
  ┌────────────────▼──────────────────────────────────────────────┐
  │     «execution environment» Serveur Base de Donnees           │
  │     IP: 159.89.13.54 (DigitalOcean Droplet)                  │
  │                                                               │
  │  ┌──────────────────────────────────────────────────────┐    │
  │  │  «container» MySQL 8.0                                │    │
  │  │  ────────────────                                     │    │
  │  │  Database: ecolearnai_db                              │    │
  │  │  User: magma                                          │    │
  │  │  Port: 3306                                           │    │
  │  │                                                       │    │
  │  │  Tables: users, subscriptions, subscription_plans,    │    │
  │  │  payments, learning_paths, learning_sessions,         │    │
  │  │  carbon_footprints, eco_compensations,                │    │
  │  │  achievements, user_achievements                      │    │
  │  └──────────────────────────────────────────────────────┘    │
  └──────────────────────────────────────────────────────────────┘
                   │
  ┌────────────────▼──────────────────────────────────────────────┐
  │     «execution environment» Serveur Backup                    │
  │     IP: 159.89.13.55 (DigitalOcean Droplet)                  │
  │                                                               │
  │  ┌──────────────────────────────────────────────────────┐    │
  │  │  «container» MySQL 8.0 (Backup)                       │    │
  │  │  ────────────────                                     │    │
  │  │  Database: ecolearnai_db_backup                       │    │
  │  │  Replication: cron quotidien 01:00 UTC                │    │
  │  │  Port: 3306                                           │    │
  │  └──────────────────────────────────────────────────────┘    │
  └──────────────────────────────────────────────────────────────┘
```

---

## 7. BPMN Camunda - Processus metier

### 7.1 Processus : Inscription et Activation du Compte

```
BPMN 2.0 - Processus d'inscription EcoLearn AI
═══════════════════════════════════════════════

Pool: [UTILISATEUR]
─────────────────────────────────────────────────────────────────────────

  (●)──►[ Remplir        ]──►[ Accepter      ]──►(X)──►[ Saisir code ]
 Start   formulaire        consentement       Gateway   OTP recu
 Event   inscription       RGPD               XOR       (SMS ou Email)
                                                │
                                                │ Code expire?
                                                │
                                                ▼
                                          [ Demander    ]──►(X)
                                            nouveau code     retour


Pool: [SYSTEME BACKEND]
─────────────────────────────────────────────────────────────────────────

  ◄──────────────────────────────────────────────────────────────────

  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │ Recevoir│    │ Valider  │    │ Generer  │    │ Chiffrer     │
  │ donnees │───>│ donnees  │───>│ code OTP │───>│ donnees RGPD │
  │ inscript│    │ (Pydantic│    │ (6 digits│    │ (Fernet AES) │
  │ ion     │    │  + RGPD) │    │  10 min) │    │              │
  └─────────┘    └────┬─────┘    └──────────┘    └──────┬───────┘
                      │                                  │
                      │ [Erreur validation]              │
                      ▼                                  ▼
                 (●) Fin                           ┌──────────┐
                 (Erreur 422)                      │ Sauver en│
                                                   │ base     │
                                                   │ (MySQL)  │
                                                   └────┬─────┘
                                                        │
                                                   ┌────▼─────┐
                                                   │ (=) Fork │
                                                   │ Parallele│
                                                   └──┬────┬──┘
                                                      │    │
                                              ┌───────┘    └───────┐
                                              ▼                    ▼
                                        ┌──────────┐        ┌──────────┐
                                        │ Envoyer  │        │ Envoyer  │
                                        │ SMS OTP  │        │ Email OTP│
                                        │(MGT-SMS) │        │ (Gmail)  │
                                        └────┬─────┘        └────┬─────┘
                                             │                    │
                                        ┌────▼────────────────────▼────┐
                                        │        (=) Join              │
                                        │        Parallele             │
                                        └─────────────┬───────────────┘
                                                      │
                                                      ▼
                                                ┌──────────┐
                                                │ Attendre │
                                                │ verif OTP│
                                                │ (Timer:  │
                                                │  10 min) │
                                                └────┬─────┘
                                                     │
                                                ┌────▼─────┐
                                                │(X)Gateway│
                                                │   XOR    │
                                                └──┬────┬──┘
                                                   │    │
                                     [Code OK]     │    │  [Code KO/expire]
                                                   │    │
                                              ┌────▼┐  ┌▼────────────┐
                                              │Activ│  │Incrementer  │
                                              │er   │  │tentatives   │
                                              │compt│  │             │
                                              │e    │  └─────┬───────┘
                                              └──┬──┘        │
                                                 │      [< 3 tentatives]
                                                 │           │
                                                 ▼           ▼
                                              (●) Fin   Retour Attente
                                              (Succes)
```

### 7.2 Processus : Paiement par Carte Bancaire

```
BPMN 2.0 - Processus de paiement carte bancaire
═══════════════════════════════════════════════════

Pool: [UTILISATEUR]
─────────────────────────────────────────────────────────────────────────

  (●)──►[ Choisir plan ]──►[ Choisir methode ]──►[ Saisir carte   ]
 Start   (mensuel/annuel)   (carte_bancaire)       sur page Umoja
                                                        │
                                                        ▼
                                                  [ Attendre     ]
                                                    confirmation


Pool: [SYSTEME BACKEND]
─────────────────────────────────────────────────────────────────────────

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │ Valider  │    │ Creer    │    │ Creer    │    │ Generer      │
  │ plan     │───>│ Abonnmt  │───>│ Paiement │───>│ ref + facture│
  │ (actif?) │    │ (INACTIF)│    │ (PENDING)│    │              │
  └──────────┘    └──────────┘    └──────────┘    └──────┬───────┘
                                                         │
                                                    ┌────▼──────┐
                                                    │ Appeler   │
                                                    │ API Umoja │
                                                    │ CardAPI   │
                                                    │ (HMAC)    │
                                                    └────┬──────┘
                                                         │
                                                    ┌────▼──────┐
                                                    │(X)Gateway │
                                                    │ Reponse?  │
                                                    └──┬─────┬──┘
                                                       │     │
                                         [OK: URL]     │     │ [Erreur]
                                                       │     │
                                                  ┌────▼┐   ┌▼────────┐
                                                  │Sauver│   │Marquer  │
                                                  │UUID +│   │paiement │
                                                  │URL   │   │= FAILED │
                                                  └──┬───┘   └────┬────┘
                                                     │             │
                                                     │             ▼
                                                     │        (●) Fin
                                                     │        (Erreur 502)
                                                     ▼
                                               ┌───────────┐
                                               │ Redirect  │
                                               │ user vers │
                                               │ page Umoja│
                                               └─────┬─────┘
                                                     │
                                                     ▼
                                               ┌───────────┐
                                               │ ⏱ Timer   │
                                               │ Attendre  │
                                               │ callback  │
                                               │ (max 30min│)
                                               └─────┬─────┘
                                                     │

Pool: [UMOJA CARDAPI]
─────────────────────────────────────────────────────────────────────────

  ┌──────────┐    ┌──────────┐    ┌──────────────────┐
  │ Afficher │    │ Traiter  │    │ Envoyer callback │
  │ page     │───>│ paiement │───>│ POST /api/       │
  │ paiement │    │ (Visa/MC)│    │ payments/moko/   │
  └──────────┘    └──────────┘    │ callback         │
                                  │ (HMAC signed)    │
                                  └────────┬─────────┘
                                           │

Pool: [SYSTEME BACKEND] (suite callback)
─────────────────────────────────────────────────────────────────────────

                                  ┌────────▼─────────┐
                                  │ Recevoir         │
                                  │ callback Umoja   │
                                  └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │ Verifier HMAC    │
                                  │ signature        │
                                  └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │(X) Gateway       │
                                  │ Status callback? │
                                  └──┬───────────┬───┘
                                     │           │
                       [ACCEPT/OK]   │           │  [REJECT/FAIL]
                                     │           │
                                ┌────▼────┐ ┌────▼─────┐
                                │ Payment │ │ Payment  │
                                │=COMPLET │ │= FAILED  │
                                │ED       │ │          │
                                └────┬────┘ └────┬─────┘
                                     │           │
                                ┌────▼────┐      │
                                │ Abonmt  │      │
                                │= ACTIF  │      │
                                └────┬────┘      │
                                     │           │
                                ┌────▼────────────▼────┐
                                │    (=) Fork          │
                                │    Parallele         │
                                └──┬──────────────┬────┘
                                   │              │
                              ┌────▼────┐   ┌────▼────┐
                              │ Envoyer │   │ Envoyer │
                              │ SMS     │   │ Email   │
                              │ notif.  │   │ notif.  │
                              └────┬────┘   └────┬────┘
                                   │              │
                              ┌────▼──────────────▼────┐
                              │    (=) Join            │
                              └───────────┬────────────┘
                                          │
                                          ▼
                                       (●) Fin
```

### 7.3 Processus : Session d'Apprentissage Complete

```
BPMN 2.0 - Processus d'apprentissage EcoLearn AI
═══════════════════════════════════════════════════

Pool: [UTILISATEUR]
─────────────────────────────────────────────────────────────────────────

  (●)──►[ Creer     ]──►[ Demarrer   ]──►[ Etudier le ]──►[ Terminer ]
 Start   parcours       session          contenu IA       session
         (sujet,        (titre)                           (score)
          difficulte)


Pool: [SYSTEME BACKEND]
─────────────────────────────────────────────────────────────────────────

  ┌──────────┐
  │ Creer    │
  │ parcours │
  │ (INSERT) │
  └────┬─────┘
       │
  ┌────▼──────┐    ┌──────────────┐    ┌──────────────┐
  │ Recevoir  │    │ Appeler      │    │ Sauver       │
  │ demande   │───>│ Flask AI     │───>│ session      │
  │ session   │    │ (OpenAI GPT) │    │ + contenu    │
  └───────────┘    └──────────────┘    └──────┬───────┘
                                              │
                                         Retour contenu au user
                                              │
                                              │ ... user etudie ...
                                              │
                                         ┌────▼──────┐
                                         │ Recevoir  │
                                         │ completion│
                                         │ (score,   │
                                         │  duree)   │
                                         └────┬──────┘
                                              │
       ┌──────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              SOUS-PROCESSUS : Post-Session                   │
  │                                                              │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
  │  │ 1.Calcul │  │ 2.Attrib │  │ 3.Maj    │  │ 4.Cumul  │   │
  │  │ empreinte│─>│ XP       │─>│ streak   │─>│ temps    │   │
  │  │ carbone  │  │ (+score) │  │ (jours   │  │ apprentis│   │
  │  │ (kWh→CO2)│  │          │  │  consec.)│  │ sage     │   │
  │  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘   │
  │                                                   │         │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │         │
  │  │ 5.Maj    │  │ 6.Verif  │  │ 7.Verif  │       │         │
  │  │ parcours │<─│ montee   │<─│ badges   │<──────┘         │
  │  │ (progress│  │ niveau   │  │ (unlock?)│                  │
  │  │  %)      │  │ auto     │  │          │                  │
  │  └────┬─────┘  └──────────┘  └──────────┘                  │
  │       │                                                     │
  │  ┌────▼─────┐                                               │
  │  │(X)Gateway│                                               │
  │  │CO2 > seuil?                                              │
  │  └──┬────┬──┘                                               │
  │     │    │                                                  │
  │ [Oui]  [Non]                                                │
  │     │    │                                                  │
  │ ┌───▼────┐ │                                                │
  │ │Compensa│ │                                                │
  │ │tion eco│ │                                                │
  │ │(planter│ │                                                │
  │ │ arbre) │ │                                                │
  │ └───┬────┘ │                                                │
  │     │      │                                                │
  │     ▼      ▼                                                │
  └─────┬──────┬────────────────────────────────────────────────┘
        │      │
        ▼      ▼
   ┌──────────────┐
   │  COMMIT      │
   │  (toutes MAJ │
   │   atomiques) │
   └──────┬───────┘
          │
          ▼
  Retour reponse enrichie
  {xp, streak, badges, carbon, level_up, compensation}
          │
          ▼
       (●) Fin
```

### 7.4 Processus : Administration des Plans

```
BPMN 2.0 - Gestion des plans d'abonnement (Admin)
═══════════════════════════════════════════════════

Pool: [ADMINISTRATEUR]
─────────────────────────────────────────────────────────────────────────

  (●)──►(X)──►[ Creer plan    ]──►[ Definir prix,  ]──►(●) Fin
 Start  Gate-  (code, nom)        duree, features
        way
        │
        ├────►[ Modifier plan  ]──►[ Changer prix   ]──►(●) Fin
        │      (select plan_id)    ou description
        │
        ├────►[ Desactiver plan]──►(X)──►[ Desactiver ]──►(●) Fin
        │                          Gate   seulement
        │                          way    (subs actives)
        │                          │
        │                          └────►[ Supprimer  ]──►(●) Fin
        │                                 definitivement
        │                                 (0 subs actives)
        │
        └────►[ Voir dashboard ]──►[ Stats globales ]──►(●) Fin
               admin               (KPIs, revenus,
                                    users, learning)
```

### 7.5 Processus global : Cycle de vie utilisateur

```
BPMN 2.0 - Cycle de vie complet d'un utilisateur EcoLearn AI
═════════════════════════════════════════════════════════════

  (●)
 Start
   │
   ▼
┌──────────────┐
│  INSCRIPTION │ ←── Sous-processus 7.1
│  + Verif OTP │
└──────┬───────┘
       │
   ┌───▼───┐
   │ Login │
   │ (JWT) │
   └───┬───┘
       │
   ┌───▼──────────────────────────────────────┐
   │          BOUCLE PRINCIPALE               │
   │                                          │
   │   ┌────────────┐                         │
   │   │(X) Gateway │                         │
   │   │ Action?    │                         │
   │   └─┬──┬──┬──┬─┘                        │
   │     │  │  │  │                           │
   │     │  │  │  └──►[ S'abonner    ] ←── 7.2│
   │     │  │  │       (plan + paiement)      │
   │     │  │  │                              │
   │     │  │  └─────►[ Apprendre    ] ←── 7.3│
   │     │  │          (parcours + sessions)  │
   │     │  │                                 │
   │     │  └────────►[ Gerer profil ]        │
   │     │             (modifier, RGPD)       │
   │     │                                    │
   │     └───────────►[ Consulter    ]        │
   │                   (dashboard, carbone)   │
   │                                          │
   │   Token expire? ──► Re-login             │
   │                                          │
   └──────────────────────────────────────────┘
       │
   ┌───▼──────┐
   │(X)Gateway│
   │ Fin?     │
   └──┬────┬──┘
      │    │
 [Desactiver] [Supprimer]
      │         │
      ▼         ▼
 ┌────────┐  ┌────────────┐
 │DESACTIV│  │SUPPRESSION │
 │E       │  │RGPD Art.17 │
 │(peut   │  │(irreversible│)
 │reactiv)│  └─────┬──────┘
 └────────┘        │
                   ▼
                (●) Fin
```

---

## 8. Legende des symboles BPMN

```
┌─────────────────────────────────────────────────────┐
│                 LEGENDE BPMN 2.0                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  (●)         Event de debut (Start Event)           │
│  (●) Fin     Event de fin (End Event)               │
│  ⏱           Timer Event (attente temporisee)       │
│                                                      │
│  [ Tache ]   Activite / Tache (Task)                │
│                                                      │
│  (X)         Gateway exclusif (XOR) - un seul chemin│
│  (=)         Gateway parallele (AND) - tous chemins │
│  (+)         Gateway inclusif (OR)                  │
│                                                      │
│  ──►         Flux de sequence                        │
│  - - ►       Flux de message (entre pools)          │
│                                                      │
│  Pool:       Participant (acteur ou systeme)         │
│  Lane:       Sous-division d'un pool                │
│                                                      │
│  ┌────────┐  Sous-processus (contient d'autres      │
│  │ [...]  │  activites)                              │
│  └────────┘                                          │
│                                                      │
│  «Service»   Tache de service (appel API)           │
│  «User»      Tache utilisateur (interaction)        │
│  «Script»    Tache script (calcul automatique)      │
└─────────────────────────────────────────────────────┘
```

---

