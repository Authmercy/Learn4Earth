import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


def build_prompt(data: dict) -> str:
    """
    Build a pedagogical prompt based on user data.

    Parameters:
    - user_level: debutant, intermediaire, avance
    - objectives: user's learning objectives
    - preferences: user's learning style preferences
    - subject: the subject to learn
    - session_title: title of the current session
    - session_number: current session number
    - total_sessions: total sessions in the path
    - difficulty: difficulty level
    """
    prompt = f"""Tu es un professeur pedagogique expert et bienveillant sur la plateforme EcoLearn AI.

CONTEXTE DE L'APPRENANT:
- Niveau : {data.get('user_level', 'debutant')}
- Objectifs : {data.get('objectives', 'Non specifies')}
- Preferences d'apprentissage : {data.get('preferences', 'Non specifiees')}

SUJET DU COURS:
- Matiere : {data.get('subject', 'Informatique')}
- Titre de la session : {data.get('session_title', 'Introduction')}
- Session {data.get('session_number', 1)} sur {data.get('total_sessions', 5)}
- Difficulte : {data.get('difficulty', 'debutant')}

INSTRUCTIONS:
1. Genere un contenu pedagogique adapte au niveau et aux preferences de l'apprenant.
2. Structure le contenu avec :
   - Un objectif clair pour cette session
   - Une explication progressive du sujet
   - Des exemples concrets et pertinents
   - Un exercice pratique
   - Un resume des points cles
3. Adapte le vocabulaire et la complexite au niveau indique.
4. Si c'est une session intermediaire, fais reference aux concepts vus precedemment.
5. Termine par une transition vers la prochaine session.
6. Utilise un ton encourageant et motivant.

Genere le contenu pedagogique maintenant :"""

    return prompt


def generate_content(data: dict) -> dict:
    """Generate pedagogical content using OpenAI GPT."""
    prompt = build_prompt(data)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant pedagogique intelligent de la plateforme EcoLearn AI. "
                        "Tu generes du contenu educatif personnalise, structure et engageant. "
                        "Reponds toujours en francais."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        return {
            "content": content,
            "prompt_used": prompt,
            "model": "gpt-3.5-turbo",
            "tokens_used": response.usage.total_tokens if response.usage else 0,
            "status": "success",
        }

    except Exception as e:
        # Fallback content when API is unavailable
        fallback_content = generate_fallback_content(data)
        return {
            "content": fallback_content,
            "prompt_used": prompt,
            "model": "fallback",
            "tokens_used": 0,
            "status": "fallback",
            "error": str(e),
        }


def generate_chat_response(data: dict) -> dict:
    """
    Generate a chatbot response using OpenAI GPT.
    Handles conversational messages from users (with or without subscription).
    """
    user_message = data.get("message", "")
    conversation_history = data.get("conversation_history", [])
    user_name = data.get("user_name", "Apprenant")
    has_subscription = data.get("has_subscription", False)

    # Build the system prompt
    system_prompt = f"""Tu es EcoBot, l'assistant intelligent de la plateforme EcoLearn AI.
Tu es bienveillant, pedagogique et tu reponds toujours en francais.

A PROPOS DE LA PLATEFORME:
- EcoLearn AI est une plateforme d'apprentissage en ligne intelligente et ecologique
- Elle propose des cours personnalises generes par IA sur differents sujets
- Elle integre un suivi d'empreinte carbone et de la gamification (XP, streaks, badges)
- Les paiements se font par carte bancaire (Visa/MC via Umoja) ou Mobile Money

L'UTILISATEUR:
- Nom : {user_name}
- Abonnement actif : {"Oui" if has_subscription else "Non"}

TES CAPACITES:
- Repondre aux questions generales sur l'apprentissage et l'education
- Expliquer des concepts dans divers domaines (programmation, sciences, langues, etc.)
- Donner des conseils d'apprentissage et de methode de travail
- Expliquer les fonctionnalites de la plateforme EcoLearn AI
- Motiver et encourager les apprenants

REGLES:
- Sois concis mais complet (max 300 mots par reponse)
- Si l'utilisateur n'a PAS d'abonnement, tu peux repondre aux questions generales mais rappelle-lui gentiment qu'un abonnement lui donne acces aux cours generes par IA, aux parcours personnalises et a la gamification complete
- Ne genere JAMAIS de cours complets (c'est reserve aux abonnes via les parcours d'apprentissage)
- Utilise des emojis avec moderation pour rendre la conversation plus vivante
"""

    # Build messages list
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (keep last 10 messages for context)
    for msg in conversation_history[-10:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    # Add current message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        return {
            "response": content,
            "tokens_used": tokens_used,
            "model": "gpt-3.5-turbo",
            "status": "success",
        }

    except Exception as e:
        # Fallback response
        fallback = (
            f"Bonjour {user_name} ! Je suis EcoBot, l'assistant de EcoLearn AI. "
            "Je rencontre un petit probleme technique en ce moment, mais je serai "
            "bientot de retour pour repondre a tes questions ! "
            "En attendant, n'hesite pas a explorer la plateforme."
        )
        if not has_subscription:
            fallback += (
                "\n\nPour acceder aux cours generes par IA et aux parcours personnalises, "
                "decouvre nos offres d'abonnement sur /api/subscriptions/plans !"
            )
        return {
            "response": fallback,
            "tokens_used": 0,
            "model": "fallback",
            "status": "fallback",
            "error": str(e),
        }


def generate_fallback_content(data: dict) -> str:
    """Generate fallback content when OpenAI API is unavailable."""
    subject = data.get("subject", "le sujet")
    title = data.get("session_title", "Introduction")
    session_num = data.get("session_number", 1)
    total = data.get("total_sessions", 5)
    level = data.get("user_level", "debutant")

    return f"""# Session {session_num}/{total} : {title}

## Objectif de la session
Comprendre les fondamentaux de {subject} adaptes au niveau {level}.

## Introduction
Bienvenue dans cette session sur **{title}** !
Cette session fait partie de votre parcours personnalise sur {subject}.

## Contenu principal

### 1. Concepts cles
Les concepts fondamentaux de {title} incluent plusieurs elements importants
que nous allons explorer ensemble dans cette session.

### 2. Exemples pratiques
Voici des exemples concrets pour illustrer les concepts abordes :
- Exemple 1 : Application directe du concept
- Exemple 2 : Cas d'utilisation reel

### 3. Exercice pratique
Mettez en pratique ce que vous avez appris en realisant l'exercice suivant.

## Resume
Dans cette session, nous avons explore les bases de {title}.
Les points cles a retenir sont les concepts fondamentaux et leur application.

## Prochaine etape
{"La prochaine session approfondira ces concepts." if session_num < total else "Felicitations ! Vous avez termine ce parcours."}

---
*Contenu genere par EcoLearn AI - Mode hors ligne*
"""
