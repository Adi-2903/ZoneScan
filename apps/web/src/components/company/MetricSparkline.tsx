"use client";

import React, { useState } from "react";

interface SparklinePoint {
  period: string;
  value: number;
}

interface MetricSparklineProps {
  title: string;
  unit: string;
  points: SparklinePoint[];
  color?: string;
  summaryText: string;
  evidenceStatus?: "disclosed" | "inferred";
  onInspectSource?: () => void;
}

export function MetricSparkline({
  title,
  unit,
  points,
  color = "#44ce9a",
  summaryText,
}: MetricSparklineProps) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  if (!points.length) return null;

  const values = points.map((p) => p.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;
  const padding = range * 0.2;
  const effectiveMin = minVal - padding;
  const effectiveMax = maxVal + padding;
  const effectiveRange = effectiveMax - effectiveMin;

  const width = 280;
  const height = 70;
  const chartPadX = 20;
  const chartPadY = 14;

  const coords = points.map((p, idx) => {
    const x = chartPadX + (idx / (points.length - 1)) * (width - chartPadX * 2);
    const y = height - chartPadY - ((p.value - effectiveMin) / effectiveRange) * (height - chartPadY * 2);
    return { x, y, point: p };
  });

  const pathD = coords.reduce((acc, curr, idx) => {
    return idx === 0 ? `M ${curr.x} ${curr.y}` : `${acc} L ${curr.x} ${curr.y}`;
  }, "");

  const areaD = `${pathD} L ${coords[coords.length - 1].x} ${height} L ${coords[0].x} ${height} Z`;

  const latest = points[points.length - 1];
  const first = points[0];
  const delta = latest.value - first.value;

  return (
    <div className="sparkline-card">
      <div className="sparkline-header">
        <div>
          <h4 className="sparkline-title">{title}</h4>
          <span className="sparkline-summary">{summaryText}</span>
        </div>
        <div className="sparkline-latest">
          <strong className="sparkline-value">{latest.value.toFixed(1)}{unit}</strong>
          <span className={`sparkline-delta ${delta >= 0 ? "positive" : "negative"}`}>
            {delta >= 0 ? "+" : ""}{delta.toFixed(1)} {unit === "%" ? "pp" : unit}
          </span>
        </div>
      </div>

      <div className="sparkline-chart-wrap" role="img" aria-label={`${title} trend chart over ${points.length} periods.`}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="sparkline-svg"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id={`spark-grad-${title.replace(/\s+/g, "-")}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.25" />
              <stop offset="100%" stopColor={color} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Background area fill */}
          <path d={areaD} fill={`url(#spark-grad-${title.replace(/\s+/g, "-")})`} />

          {/* Line */}
          <path
            d={pathD}
            fill="none"
            stroke={color}
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {coords.map((c, i) => (
            <g key={c.point.period}>
              <circle
                cx={c.x}
                cy={c.y}
                r={hoveredIdx === i ? "4.5" : "3"}
                fill={color}
                stroke="var(--surface)"
                strokeWidth="1.5"
                className="sparkline-point"
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
              />
            </g>
          ))}
        </svg>

        {/* Hover pill */}
        {hoveredIdx !== null && (
          <div
            className="sparkline-tooltip"
            style={{
              left: `${(coords[hoveredIdx].x / width) * 100}%`,
              transform: "translateX(-50%)",
            }}
          >
            <strong>{coords[hoveredIdx].point.period}</strong>: {coords[hoveredIdx].point.value.toFixed(2)}{unit}
          </div>
        )}
      </div>

      {/* Axis labels */}
      <div className="sparkline-periods" aria-hidden="true">
        {points.map((p, i) => (
          <span
            key={p.period}
            className={`period-tag ${i === points.length - 1 ? "active" : ""}`}
            onMouseEnter={() => setHoveredIdx(i)}
            onMouseLeave={() => setHoveredIdx(null)}
          >
            {p.period}
          </span>
        ))}
      </div>

      {/* Accessible Table representation */}
      <details className="sparkline-accessible-table">
        <summary>View {title} data table</summary>
        <table>
          <thead>
            <tr>
              <th scope="col">Period</th>
              <th scope="col">Value ({unit})</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p) => (
              <tr key={p.period}>
                <td>{p.period}</td>
                <td>{p.value.toFixed(2)} {unit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
