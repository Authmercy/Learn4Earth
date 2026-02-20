import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.gpt_service import generate_content, generate_chat_response

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "EcoLearn AI - Service IA",
        "version": "1.0.0",
        "status": "running",
        "description": "API Flask pour la generation de contenu pedagogique adaptatif via OpenAI GPT",
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/generate", methods=["POST"])
def generate():
    """
    Generate adaptive pedagogical content.

    Expected JSON body:
    {
        "user_level": "debutant|intermediaire|avance",
        "objectives": "string",
        "preferences": "string",
        "subject": "string",
        "session_title": "string",
        "session_number": int,
        "total_sessions": int,
        "difficulty": "string"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Donnees JSON requises"}), 400

    required_fields = ["subject", "session_title"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Champ requis manquant: {field}"}), 400

    result = generate_content(data)
    return jsonify(result)


@app.route("/chat", methods=["POST"])
def chat():
    """
    Chatbot IA conversationnel.
    Repond aux questions generales sur l'apprentissage et la plateforme.
    Accessible a tous les utilisateurs (avec ou sans abonnement).

    Expected JSON body:
    {
        "message": "string",
        "conversation_history": [
            {"role": "user", "content": "string"},
            {"role": "assistant", "content": "string"}
        ],
        "user_name": "string (optional)",
        "has_subscription": bool
    }
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Le champ 'message' est requis"}), 400

    result = generate_chat_response(data)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
