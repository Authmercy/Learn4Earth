import Hero from "../../Components/Dashboard/Hero.jsx";
import Filters from "../../Components/Dashboard/Filters.jsx";
import KpiCard from "../../Components/Dashboard/KpiCard.jsx";
import AreaChart from "../../Components/Dashboard/AreaChart.jsx";
import DonutChart from "../../Components/Dashboard/DonutChart.jsx";

import useCarbonData from "../../hooks/useCarbonData.js";

export default function Dashboard() {
  const { loading, error, carbon } = useCarbonData();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Chargement des données carbone...
      </div>
    );
  }

  if (error || !carbon) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">
        {error || "Erreur inconnue"}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 px-6 md:px-12 py-10 font-poppins">

      {/* HERO */}
      <div className="mb-10">
        <Hero
          data={[
            { label: "CO₂ total généré", value: carbon.hero.total },
            { label: "CO₂ compensé", value: carbon.hero.compensated },
            { label: "Arbres plantés", value: carbon.hero.trees },
          ]}
        />
      </div>

      {/* FILTERS */}
      <div className="mb-8">
        <Filters />
      </div>

      {/* KPI CARDS */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {carbon.kpis.map((kpi, i) => (
          <KpiCard key={i} {...kpi} />
        ))}
      </div>

      {/* CHARTS */}
      <div className="grid lg:grid-cols-2 gap-10">

        {/* AREA CHART */}
        <div className="bg-white shadow-xl rounded-2xl p-6 border border-white/40">
          <AreaChart data={carbon.area} />
        </div>

        {/* DONUT CHARTS */}
        <div className="grid sm:grid-cols-2 gap-6">

          <div className="bg-white shadow-xl rounded-2xl p-6 border border-white/40">
            <DonutChart
              title="Répartition des émissions"
              data={carbon.donut_category}
              colors={["#b7e1b0", "#66bb6a", "#2e7d32"]}
            />
          </div>

          <div className="bg-white shadow-xl rounded-2xl p-6 border border-white/40">
            <DonutChart
              title="Scopes carbone"
              data={carbon.donut_scope}
              colors={["#c8e6c9", "#81c784", "#2e7d32"]}
            />
          </div>

        </div>
      </div>
    </div>
  );
}
