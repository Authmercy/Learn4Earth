import * as d3 from "d3";
import { useEffect, useRef } from "react";

export default function AreaChart({ data }) {
  const ref = useRef();

  useEffect(() => {
    const width = 540; // un peu plus large pour Dec
    const height = 300;

    const margin = {
      top: 60,     // ⬆️ place pour la légende
      right: 50,   // ⬅️ évite que Dec soit coupé
      bottom: 50,
      left: 28,
    };

    d3.select(ref.current).selectAll("*").remove();

    const svg = d3
      .select(ref.current)
      .attr("width", width)
      .attr("height", height);

    const keys = ["energy", "transport", "waste"];

    const labels = [
      { key: "energy", label: "Energy", color: "#b7e1b0" },
      { key: "transport", label: "Transportation", color: "#66bb6a" },
      { key: "waste", label: "Waste", color: "#2e7d32" },
    ];

    /* ================= STACK ================= */
    const stack = d3.stack().keys(keys);
    const stackedData = stack(data);

    /* ================= SCALES ================= */

    // X : mois bien espacés + Dec visible
    const x = d3
    .scalePoint()
    .domain(data.map(d => d.month))
    .range([margin.left, width - margin.right]);
  
    // Y : valeurs contenues
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(stackedData[2], d => d[1])])
      .nice()
      .range([height - margin.bottom, margin.top]);

    /* ================= AREA ================= */
    const area = d3
      .area()
      .x(d => x(d.data.month))
      .y0(d => y(d[0]))
      .y1(d => y(d[1]))
      .curve(d3.curveMonotoneX);

    svg
      .append("g")
      .selectAll("path")
      .data(stackedData)
      .enter()
      .append("path")
      .attr("fill", (_, i) => labels[i].color)
      .attr("d", area);

    /* ================= AXES ================= */

    // Axe X (Jan → Dec)
    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("font-size", "11px");

    // Axe Y
    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).ticks(5))
      .selectAll("text")
      .style("font-size", "11px");

    /* ================= LÉGENDE EN HAUT ================= */

    const legend = svg
      .append("g")
      .attr("transform", `translate(${width / 2 - 170}, 20)`);

    labels.forEach((item, i) => {
      const g = legend
        .append("g")
        .attr("transform", `translate(${i * 140},0)`);

      g.append("rect")
        .attr("width", 14)
        .attr("height", 14)
        .attr("rx", 3)
        .attr("fill", item.color);

      g.append("text")
        .attr("x", 20)
        .attr("y", 12)
        .text(item.label)
        .style("font-size", "12px")
        .style("fill", "#374151");
    });
  }, [data]);

  return (
    <div className="chart-card">
      <h3>Emissions over Time</h3>
      <svg ref={ref} />
    </div>
  );
}
