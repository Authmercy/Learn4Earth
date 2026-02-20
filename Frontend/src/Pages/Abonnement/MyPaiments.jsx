import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function MyPayments() {
  const token = localStorage.getItem("access_token");
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    const load = async () => {
      const res = await fetch("http://206.189.56.166:8000/api/payments/my", {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();
      if (res.status === 200) setPayments(data);
    };

    load();
  }, [token]);

  return (
    <div className="min-h-screen px-6 py-10 bg-gradient-to-br from-green-50 to-blue-100">
      <h1 className="text-3xl font-bold text-green-800 mb-8">Mes paiements</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {payments.map((p) => (
          <div key={p.id} className="bg-white shadow-lg rounded-xl p-6">
            <p className="text-lg font-semibold">Paiement #{p.id}</p>
            <p className="text-gray-600 mt-2">{p.amount} €</p>
            <p className="text-gray-600">Statut : {p.status}</p>

            <div className="flex gap-4 mt-4">
              <Link
                to={`/invoice/${p.id}`}
                className="text-green-700 underline"
              >
                Voir facture
              </Link>

              <Link
                to={`/payment-status/${p.id}`}
                className="text-blue-700 underline"
              >
                Vérifier statut
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
