import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function PaymentCallback() {
  const token = localStorage.getItem("access_token");
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const paymentId = params.get("payment_id");
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(
          `http://206.189.56.166:8000/api/payments/${paymentId}/status`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const data = await res.json();

        if (res.status === 200) {
          setStatus(data.status);
        } else {
          setStatus("error");
        }
      } catch {
        setStatus("error");
      }
    };

    if (paymentId) checkStatus();
  }, [paymentId, token]);

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Vérification du paiement...
      </div>
    );
  }

  if (status === "confirmed") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center px-6">
        <h1 className="text-4xl font-bold text-green-700 mb-4">
          Paiement confirmé 🎉
        </h1>
        <p className="text-gray-700 mb-6">
          Votre abonnement EcoLearnAI est maintenant actif.
        </p>

        <button
          onClick={() => navigate("/plans")}
          className="px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
        >
          Voir mon abonnement
        </button>
      </div>
    );
  }

  if (status === "failed") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center px-6">
        <h1 className="text-4xl font-bold text-red-600 mb-4">
          Paiement échoué ❌
        </h1>
        <p className="text-gray-700 mb-6">
          Le paiement n’a pas pu être validé. Vous pouvez réessayer.
        </p>

        <button
          onClick={() => navigate("/plans")}
          className="px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
        >
          Retour aux abonnements
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-6">
      <h1 className="text-4xl font-bold text-gray-700 mb-4">
        Paiement en attente ⏳
      </h1>
      <p className="text-gray-700 mb-6">
        Nous attendons la confirmation du paiement.
      </p>

      <button
        onClick={() => navigate("/plans")}
        className="px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
      >
        Retour aux abonnements
      </button>
    </div>
  );
}
