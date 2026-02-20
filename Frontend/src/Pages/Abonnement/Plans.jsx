import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import PricingCard from "../../Components/Pricing/PricingCard";

export default function Plans() {
  const token = localStorage.getItem("access_token");
  const navigate = useNavigate();

  const [plans, setPlans] = useState([]);
  const [currentSub, setCurrentSub] = useState(null);
  const [loading, setLoading] = useState(true);

  const offersRef = useRef(null);

  const scrollToOffers = () => {
    offersRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const load = async () => {
      try {
        // 1️⃣ Charger l'abonnement actuel
        const subRes = await fetch(
          "http://206.189.56.166:8000/api/subscriptions/my",
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (subRes.status === 200) {
          const subData = await subRes.json();
          if (subData && subData.plan_name) {
            setCurrentSub(subData);
          }
        }

        // 2️⃣ Charger les plans disponibles
        const plansRes = await fetch(
          "http://206.189.56.166:8000/api/subscriptions/plans",
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const data = await plansRes.json();

        if (plansRes.status === 200 && data.plans) {
          setPlans(data.plans);
        }
      } catch (err) {
        console.error("Erreur chargement abonnements/plans", err);
      }

      setLoading(false);
    };

    load();
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Chargement...
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10 bg-gradient-to-br from-green-50 to-blue-100">

      {/* ----------------------------- */}
      {/* ABONNEMENT ACTUEL */}
      {/* ----------------------------- */}

      <h1 className="text-3xl font-bold text-green-800 mb-6">
        Mon abonnement
      </h1>

      {!currentSub ? (
        <div className="bg-white shadow-lg rounded-2xl p-8 mb-12 border border-green-200">
          <h2 className="text-xl font-semibold text-gray-700">
            Mon abonnement actuel : <span className="font-bold">Aucun</span>
          </h2>

          <p className="text-gray-600 mt-2">
            Vous n’avez pas encore souscrit à un plan EcoLearnAI.
          </p>

          <button
            onClick={scrollToOffers}
            className="mt-6 px-5 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
          >
            Souscrire
          </button>
        </div>
      ) : (
        <div className="bg-white shadow-lg rounded-2xl p-8 mb-12 border border-green-200">
          <h2 className="text-2xl font-semibold text-green-700">
            {currentSub.plan_name}
          </h2>

          <p className="text-gray-600 mt-2">
            Statut : <span className="font-semibold">{currentSub.status}</span>
          </p>

          <p className="text-gray-600 mt-1">
            Renouvellement :{" "}
            <span className="font-semibold">{currentSub.renewal_date}</span>
          </p>

          <div className="flex gap-4 mt-6">
            <button
              onClick={scrollToOffers}
              className="px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
            >
              Changer d’abonnement
            </button>

            <button
              onClick={() => alert("Résiliation à implémenter")}
              className="px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition"
            >
              Résilier
            </button>
          </div>
        </div>
      )}

      {/* ----------------------------- */}
      {/* OFFRES DISPONIBLES */}
      {/* ----------------------------- */}

      <div ref={offersRef}>
        <h2 className="text-3xl font-bold text-green-800 mb-8">
          Offres disponibles
        </h2>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((p, index) => {
            const isAnnual = p.duration_days >= 365;

            return (
              <PricingCard
                key={p.code}
                code={p.code}
                plan={p.name}
                price={p.price}
                duration={isAnnual ? "an" : "mois"}
                description={p.description || "Accès complet à EcoLearnAI"}
                features={[
                  { text: "Cours illimités", included: true },
                  { text: "Support prioritaire", included: true },
                  { text: "Statistiques avancées", included: isAnnual },
                ]}
                highlighted={isAnnual}
                delay={index * 100}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
