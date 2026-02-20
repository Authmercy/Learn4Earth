import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function Invoice() {
  const { payment_id } = useParams();
  const token = localStorage.getItem("access_token");

  const [invoice, setInvoice] = useState(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(
        `http://206.189.56.166:8000/api/payments/${payment_id}/invoice`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const data = await res.json();
      if (res.status === 200) setInvoice(data);
    };

    load();
  }, [payment_id, token]);

  if (!invoice) {
    return <div className="min-h-screen flex items-center justify-center">Chargement...</div>;
  }

  return (
    <div className="min-h-screen px-6 py-10">
      <h1 className="text-3xl font-bold mb-6">Facture #{payment_id}</h1>

      <pre className="bg-gray-100 p-6 rounded-xl">
        {JSON.stringify(invoice, null, 2)}
      </pre>
    </div>
  );
}
