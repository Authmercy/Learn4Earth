import * as d3 from "d3";
import { useEffect, useRef } from "react";

export default function DonutChart({ title, data, colors }) {
  const ref = useRef();

  useEffect(() => {
    const width = 200;
    const height = 200;
    const radius = Math.min(width, height) / 2;

    d3.select(ref.current).selectAll("*").remove();

    const svg = d3
      .select(ref.current)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const pie = d3
      .pie()
      .sort(null)
      .value(d => d.value);

    const arc = d3
      .arc()
      .innerRadius(radius * 0.65)
      .outerRadius(radius);

    svg
      .selectAll("path")
      .data(pie(data))
      .enter()
      .append("path")
      .attr("d", arc)
      .attr("fill", (_, i) => colors[i])
      .attr("stroke", "#fff")
      .style("stroke-width", "2px");
  }, [data, colors]);

  return (
    <div className="chart-card donut-card">
      <h3>{title}</h3>

      <div className="donut-wrapper">
        <svg ref={ref} className="donut" />
      </div>

      <div className="donut-legend">
        {data.map((d, i) => (
          <div key={i} className="legend-item">
            <span
              className="legend-color"
              style={{ backgroundColor: colors[i] }}
            />
            {d.label} — {d.value}%
          </div>
        ))}
      </div>
    </div>
  );
}
