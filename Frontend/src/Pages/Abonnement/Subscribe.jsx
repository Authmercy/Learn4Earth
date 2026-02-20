import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useState } from "react";

export default function Subscribe() {
  const { plan_code } = useParams();
  const token = localStorage.getItem("access_token");
  const navigate = useNavigate();

  const plan = useLocation().state;

  const [paymentMethod, setPaymentMethod] = useState("carte_bancaire");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const subscribe = async () => {
    setLoading(true);
    setApiError("");

    try {
      const res = await fetch("http://206.189.56.166:8000/api/subscriptions/subscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          plan: plan_code,
          payment_method: paymentMethod,
        }),
      });

      const data = await res.json();

      // 1️⃣ Carte bancaire → redirection Moko
      if (paymentMethod === "carte_bancaire") {
        if (data?.payment_url) {
          window.location.href = data.payment_url;
          return;
        }
      }

      // 2️⃣ Mobile Money → abonnement activé immédiatement
      if (paymentMethod === "mobile_money") {
        navigate("/plans", { state: { success: true } });
        return;
      }

      // 3️⃣ Erreur API
      setApiError(JSON.stringify(data, null, 2));
    } catch (err) {
      setApiError("Erreur serveur");
    }

    setLoading(false);
  };

  if (!plan) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Plan introuvable
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10 bg-gradient-to-br from-green-50 to-blue-100">
      <div className="max-w-xl mx-auto bg-white shadow-xl rounded-2xl p-10">

        <h1 className="text-3xl font-bold text-green-800 mb-6">
          Souscrire à {plan.plan}
        </h1>

        <p className="text-gray-700 mb-4">{plan.description}</p>

        <p className="text-2xl font-bold text-green-700 mb-8">
          {plan.price} € / {plan.duration}
        </p>

        {/* Méthode de paiement */}
        <div className="mb-6">
          <label className="text-gray-700 font-semibold">Méthode de paiement</label>
          <select
            className="w-full border p-3 rounded-lg mt-2"
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
          >
            <option value="carte_bancaire">Carte bancaire (Visa, Mastercard)</option>
            <option value="mobile_money">Mobile Money (Orange, MTN, Airtel, Wave)</option>
          </select>
        </div>

        {apiError && (
          <pre className="text-red-600 text-sm bg-red-50 p-3 rounded-lg mb-4">
            {apiError}
          </pre>
        )}

        <button
          onClick={subscribe}
          disabled={loading}
          className="w-full bg-green-700 text-white py-3 rounded-lg font-semibold hover:bg-green-800 transition"
        >
          {loading ? "Traitement..." : "Confirmer l’abonnement"}
        </button>
      </div>
    </div>
  );
}
