import { useEffect, useState } from "react";

export default function MySubscription() {
  const token = localStorage.getItem("access_token");
  const [sub, setSub] = useState(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch("http://206.189.56.166:8000/api/subscriptions/my", {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();
      if (res.status === 200) setSub(data);
    };

    load();
  }, [token]);

  if (!sub) {
    return <div className="min-h-screen flex items-center justify-center">Aucun abonnement actif</div>;
  }

  return (
    <div className="min-h-screen px-6 py-10 bg-gradient-to-br from-green-50 to-blue-100">
      <div className="max-w-xl mx-auto bg-white shadow-xl rounded-2xl p-10">
        <h1 className="text-3xl font-bold text-green-800 mb-6">Mon abonnement</h1>

        <p className="text-xl font-semibold">{sub.plan_name}</p>
        <p className="text-gray-600 mt-2">Statut : {sub.status}</p>
        <p className="text-gray-600 mt-2">Renouvellement : {sub.renewal_date}</p>
      </div>
    </div>
  );
}
