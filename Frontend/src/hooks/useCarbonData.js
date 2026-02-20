import { useEffect, useState } from "react";

export default function useCarbonData() {
  const token = localStorage.getItem("access_token");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [carbon, setCarbon] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        // SUMMARY
        const s = await fetch("http://206.189.56.166:8000/api/carbon/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const summary = s.ok ? await s.json() : null;

        // FOOTPRINTS
        const f = await fetch("http://206.189.56.166:8000/api/carbon/footprints", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const footprints = f.ok ? await f.json() : [];

        // COMPENSATIONS
        const c = await fetch("http://206.189.56.166:8000/api/carbon/compensations", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const compensations = c.ok ? await c.json() : [];

        if (!summary) {
          setError("Impossible de charger les données carbone");
          setLoading(false);
          return;
        }

        // ============================
        // 🔥 TRANSFORMATION DES DONNÉES
        // ============================

        // HERO KPIs
        const hero = {
          total: summary.total_carbon_kg,
          compensated: summary.total_co2_compensated_kg,
          trees: summary.total_trees_planted,
        };

        // KPI CARDS
        const kpis = [
          { title: "CO₂ total généré", value: summary.total_carbon_kg, target: 20000 },
          { title: "CO₂ compensé", value: summary.total_co2_compensated_kg, target: summary.total_carbon_kg },
          { title: "Arbres plantés", value: summary.total_trees_planted, target: 500 },
          { title: "Prochaine compensation", value: summary.next_compensation_in_kg, target: 1000 },
        ];

        // AREA CHART (par mois)
        const area = footprints.map((f) => ({
          month: new Date(f.created_at).toLocaleString("fr-FR", { month: "short" }),
          energy: f.energy_kwh,
          transport: f.duration_minutes,
          waste: f.carbon_kg,
        }));

        // DONUT CATEGORY
        const donut_category = [
          { label: "Énergie (kWh)", value: footprints.reduce((a, b) => a + b.energy_kwh, 0) },
          { label: "Durée (min)", value: footprints.reduce((a, b) => a + b.duration_minutes, 0) },
          { label: "CO₂ (kg)", value: footprints.reduce((a, b) => a + b.carbon_kg, 0) },
        ];

        // DONUT SCOPE (mock basé sur tes données)
        const donut_scope = [
          { label: "Scope 1", value: summary.total_carbon_kg * 0.35 },
          { label: "Scope 2", value: summary.total_carbon_kg * 0.45 },
          { label: "Scope 3", value: summary.total_carbon_kg * 0.20 },
        ];

        setCarbon({
          hero,
          kpis,
          area,
          donut_category,
          donut_scope,
        });

      } catch (err) {
        setError("Erreur serveur");
      }

      setLoading(false);
    };

    load();
  }, [token]);

  return { loading, error, carbon };
}
