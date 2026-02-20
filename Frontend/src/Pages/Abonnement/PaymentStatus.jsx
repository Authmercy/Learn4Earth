import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function PaymentStatus() {
  const { payment_id } = useParams();
  const token = localStorage.getItem("access_token");

  const [status, setStatus] = useState(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(
        `http://206.189.56.166:8000/api/payments/${payment_id}/status`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const data = await res.json();
      if (res.status === 200) setStatus(data);
    };

    load();
  }, [payment_id, token]);

  if (!status) {
    return <div className="min-h-screen flex items-center justify-center">Chargement...</div>;
  }

  return (
    <div className="min-h-screen px-6 py-10">
      <h1 className="text-3xl font-bold mb-6">Statut du paiement</h1>

      <pre className="bg-gray-100 p-6 rounded-xl">
        {JSON.stringify(status, null, 2)}
      </pre>
    </div>
  );
}
