export default function KpiCard({ title, value, target }) {
    const percent = Math.min((value / target) * 100, 100);
  
    return (
      <div className="kpi-card">
        <h4>{title}</h4>
        <strong>{value.toLocaleString()} tCO₂e</strong>
        <div className="progress">
          <div style={{ width: `${percent}%` }} />
        </div>
        <small>Target {target.toLocaleString()}</small>
        <span className="badge">100% reporting</span>
      </div>
    );
  }
  