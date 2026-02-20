import { useEffect, useState } from "react";
import PricingCard from "../Components/Pricing/PricingCard";

export default function Pricing() {
  const [isMonthly, setIsMonthly] = useState(true);
  const [plans, setPlans] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPlans = async () => {
      try {
        const res = await fetch("http://206.189.56.166:8000/api/subscriptions/plans");
        const data = await res.json();

        if (res.status === 200) {
          setPlans(data.plans);
          setPaymentMethods(data.payment_methods);
        }
      } catch (err) {
        console.error("Erreur chargement plans", err);
      }

      setLoading(false);
    };

    loadPlans();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Chargement des plans...
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-72 h-72 bg-accent-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* HEADER */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-display font-bold mb-6 animate-slide-up">
          Des tarifs <span className="gradient-text">simples</span> et{" "}
          <span className="gradient-text">flexibles</span>
        </h1>

        <p className="text-xl text-dark-600 dark:text-dark-300 max-w-2xl mx-auto mb-12 animate-slide-up animate-delay-100">
          Choisissez le plan qui correspond à vos besoins. Changez ou annulez à tout moment.
        </p>

        {/* TOGGLE */}
        <div className="flex items-center justify-center gap-4 mb-16 animate-slide-up animate-delay-200">
          <button
            onClick={() => setIsMonthly(true)}
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
              isMonthly
                ? "bg-primary-500 text-white shadow-glow"
                : "text-dark-600 dark:text-dark-400 hover:bg-gray-100 dark:hover:bg-dark-800"
            }`}
          >
            Mensuel
          </button>

          <button
            onClick={() => setIsMonthly(false)}
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 relative ${
              !isMonthly
                ? "bg-primary-500 text-white shadow-glow"
                : "text-dark-600 dark:text-dark-400 hover:bg-gray-100 dark:hover:bg-dark-800"
            }`}
          >
            Annuel
            <span className="absolute -top-2 -right-2 bg-accent-500 text-white text-xs px-2 py-1 rounded-full">
              -20%
            </span>
          </button>
        </div>

        {/* PLANS */}
        <div className="grid md:grid-cols-2 gap-8 max-w-7xl mx-auto">
          {plans.map((plan, index) => {
            const price = isMonthly
              ? plan.duration_days === 30
                ? plan.price
                : Math.round(plan.price / 12)
              : plan.price;

            return (
              <PricingCard
                key={plan.code}
                plan={plan.name}
                price={price}
                duration={isMonthly ? "mois" : "an"}
                description={plan.description || "Accès complet à la plateforme"}
                features={[
                  { text: "Cours illimités", included: true },
                  { text: "Support premium", included: true },
                ]}
                highlighted={plan.code === "annuel"}
                delay={index * 100}
              />
            );
          })}
        </div>
      </section>

      {/* PAYMENT METHODS */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl font-display font-bold text-center mb-12">
            Méthodes de paiement
          </h2>

          <div className="space-y-4">
            {paymentMethods.map((pm, index) => (
              <div key={index} className="card p-6">
                <p className="font-semibold text-lg">{pm.label}</p>
                {pm.provider && (
                  <p className="text-dark-600 dark:text-dark-400 text-sm">
                    Fournisseur : {pm.provider}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
