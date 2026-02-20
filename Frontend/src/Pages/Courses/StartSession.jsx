import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function StartSession() {
  const { id } = useParams(); // learning_path_id
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");
  const [subscriptionPopup, setSubscriptionPopup] = useState(false);

  useEffect(() => {
    const start = async () => {
      try {
        // 1️⃣ Récupérer toutes les sessions
        const listRes = await fetch(
          "http://206.189.56.166:8000/api/learning/sessions",
          { headers: { Authorization: `Bearer ${token}` } }
        );

        // 🔐 Token expiré
        if (listRes.status === 401) {
          localStorage.clear();
          navigate("/login");
          return;
        }

        // 🔥 Abonnement requis
        if (listRes.status === 403) {
          setSubscriptionPopup(true);
          return;
        }

        if (listRes.status !== 200) {
          setApiError("Impossible de récupérer les sessions.");
          return;
        }

        const allSessions = await listRes.json();
        const sessionsForPath = allSessions.filter(
          (s) => String(s.learning_path_id) === String(id)
        );

        const nextNumber = sessionsForPath.length + 1;

        // 2️⃣ Générer la session suivante
        const res = await fetch(
          "http://206.189.56.166:8000/api/learning/sessions",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              learning_path_id: id,
              title: `Session ${nextNumber}`,
              session_number: nextNumber,
            }),
          }
        );

        // 🔐 Token expiré
        if (res.status === 401) {
          localStorage.clear();
          navigate("/login");
          return;
        }

        // 🔥 Abonnement requis
        if (res.status === 403) {
          setSubscriptionPopup(true);
          return;
        }

        const data = await res.json();

        if (res.status === 201) {
          navigate(`/session/${data.id}`, { state: data });
          return;
        }

        setApiError(JSON.stringify(data, null, 2));
      } catch {
        setApiError("Erreur serveur");
      }

      setLoading(false);
    };

    start();
  }, [id, token, navigate]);

  // 🔥 Popup abonnement premium
  if (subscriptionPopup) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black/40 backdrop-blur-sm px-6">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-sm text-center">
          <h2 className="text-xl font-bold text-red-600 mb-3">
            Abonnement requis
          </h2>
          <p className="text-gray-700 mb-6">
            Vous devez souscrire à un abonnement actif pour générer une session.
          </p>
          <button
            onClick={() => navigate("/plans")}
            className="bg-green-700 text-white px-6 py-3 rounded-lg hover:bg-green-800 transition"
          >
            Voir les abonnements
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Génération de la session...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center text-red-600 whitespace-pre-wrap px-6">
      {apiError}
    </div>
  );
}
