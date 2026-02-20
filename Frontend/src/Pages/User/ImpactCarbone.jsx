import { useEffect, useState } from "react";

export default function ImpactCarbone() {
  const token = localStorage.getItem("access_token");

  const [summary, setSummary] = useState(null);
  const [footprints, setFootprints] = useState([]);
  const [compensations, setCompensations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        // Résumé global
        const s = await fetch("http://206.189.56.166:8000/api/carbon/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (s.status === 200) setSummary(await s.json());

        // Empreintes carbone
        const f = await fetch("http://206.189.56.166:8000/api/carbon/footprints", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (f.status === 200) setFootprints(await f.json());

        // Compensations
        const c = await fetch("http://206.189.56.166:8000/api/carbon/compensations", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (c.status === 200) setCompensations(await c.json());
      } catch (err) {
        console.error("Erreur impact carbone", err);
      }

      setLoading(false);
    };

    load();
  }, [token]);

  if (loading || !summary) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Chargement de votre impact carbone...
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10 bg-gradient-to-br from-green-50 to-blue-100">

      {/* ----------------------------- */}
      {/* HEADER */}
      {/* ----------------------------- */}

      <h1 className="text-4xl font-bold text-green-800 mb-10">
        Impact Carbone 🌍
      </h1>

      {/* ----------------------------- */}
      {/* RÉSUMÉ GLOBAL */}
      {/* ----------------------------- */}

      <div className="bg-white shadow-xl rounded-2xl p-8 mb-12 border border-green-200">
        <h2 className="text-2xl font-semibold text-green-700 mb-6">
          Vue d’ensemble
        </h2>

        <div className="grid md:grid-cols-3 gap-6">

          <div className="p-6 bg-green-50 rounded-xl border border-green-200">
            <p className="text-sm text-gray-600">CO₂ total généré</p>
            <p className="text-3xl font-bold text-green-800">
              {summary.total_carbon_kg} kg
            </p>
          </div>

          <div className="p-6 bg-blue-50 rounded-xl border border-blue-200">
            <p className="text-sm text-gray-600">CO₂ compensé</p>
            <p className="text-3xl font-bold text-blue-800">
              {summary.total_co2_compensated_kg} kg
            </p>
          </div>

          <div className="p-6 bg-yellow-50 rounded-xl border border-yellow-200">
            <p className="text-sm text-gray-600">Arbres plantés</p>
            <p className="text-3xl font-bold text-yellow-800">
              {summary.total_trees_planted}
            </p>
          </div>

        </div>

        <div className="mt-6 text-gray-700">
          <p className="font-semibold">
            Prochaine compensation dans :{" "}
            <span className="text-green-700">
              {summary.next_compensation_in_kg} kg CO₂
            </span>
          </p>
        </div>
      </div>

      {/* ----------------------------- */}
      {/* EMPREINTES CARBONE */}
      {/* ----------------------------- */}

      <h2 className="text-3xl font-bold text-green-800 mb-4">
        Empreinte carbone par session
      </h2>

      <div className="bg-white shadow-lg rounded-2xl p-6 mb-12 border border-gray-200 max-h-[350px] overflow-y-auto">
        {footprints.length === 0 && (
          <p className="text-gray-600">Aucune activité enregistrée.</p>
        )}

        <ul className="space-y-4">
          {footprints.map((f) => (
            <li
              key={f.id}
              className="p-4 rounded-xl border bg-gray-50 hover:bg-gray-100 transition"
            >
              <p className="text-lg font-semibold text-green-700">
                Session {f.session_id}
              </p>

              <p className="text-gray-600 text-sm">
                {new Date(f.created_at).toLocaleString()}
              </p>

              <div className="mt-2 flex gap-6 text-sm">
                <span className="text-gray-700">
                  ⏱ {f.duration_minutes} min
                </span>
                <span className="text-gray-700">
                  ⚡ {f.energy_kwh} kWh
                </span>
                <span className="font-bold text-green-700">
                  🌱 {f.carbon_kg} kg CO₂
                </span>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* ----------------------------- */}
      {/* COMPENSATIONS */}
      {/* ----------------------------- */}

      <h2 className="text-3xl font-bold text-green-800 mb-4">
        Compensations écologiques
      </h2>

      <div className="bg-white shadow-lg rounded-2xl p-6 border border-gray-200 max-h-[350px] overflow-y-auto">
        {compensations.length === 0 && (
          <p className="text-gray-600">Aucune compensation effectuée.</p>
        )}

        <ul className="space-y-4">
          {compensations.map((c) => (
            <li
              key={c.id}
              className="p-4 rounded-xl border bg-green-50 hover:bg-green-100 transition"
            >
              <p className="text-lg font-semibold text-green-800">
                {c.partner_name}
              </p>

              <p className="text-gray-600 text-sm">
                {new Date(c.triggered_at).toLocaleString()}
              </p>

              <div className="mt-2 flex gap-6 text-sm">
                <span className="font-bold text-green-700">
                  🌳 {c.trees_planted} arbres
                </span>
                <span className="font-bold text-blue-700">
                  ♻ {c.co2_compensated_kg} kg CO₂ compensés
                </span>
              </div>

              <p className="text-xs text-gray-500 mt-2">
                Statut : {c.status}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
