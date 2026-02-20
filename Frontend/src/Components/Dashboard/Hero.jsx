import heroImg from "../../assets/hero-illustration.svg";

export default function Hero({ data }) {
  return (
    <div className="hero">
      <div className="hero-left">
        <h1>Sustainability KPI Dashboard</h1>

        <div className="hero-kpis">
          {data.map((item, i) => (
            <div key={i} className="hero-kpi">
              <span>{item.label}</span>
              <strong>{item.value.toLocaleString()}</strong>
              <small>tCO₂e</small>
            </div>
          ))}
        </div>
      </div>

      <div className="hero-right">
        <img src={heroImg} alt="Sustainability illustration" />
      </div>
    </div>
  );
}
