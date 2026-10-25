"use client";

import { useMemo, useState } from "react";
import type { Candle, LiquidityLevel, Zone } from "@/lib/api";

type Props = { candles: Candle[]; zones: Zone[]; levels: LiquidityLevel[]; timeframe: string };

export function ZoneChart({ candles, zones, levels, timeframe }: Props) {
  const [showZones, setShowZones] = useState(true);
  const [showLevels, setShowLevels] = useState(true);
  const view = useMemo(() => {
    const usable = candles.filter((item) => item.complete);
    const selected = usable.slice(-80);
    const min = Math.min(...selected.map((item) => item.low));
    const max = Math.max(...selected.map((item) => item.high));
    const range = max - min || 1;
    const width = Math.max(680, selected.length * 11 + 72);
    const height = 300;
    const top = 18;
    const bottom = 32;
    const chartHeight = height - top - bottom;
    const y = (price: number) => top + (max - price) / range * chartHeight;
    return { selected, min, max, width, height, chartHeight, top, bottom, y };
  }, [candles]);

  const activeZones = zones.filter((zone) => zone.active && ["fresh", "tested"].includes(zone.state))
    .slice(-8);
  const visibleLevels = levels.filter((level) => level.state === "unswept").slice(-8);
  if (!view.selected.length) {
    return <div className="empty-chart">No completed {timeframe} candles are available for this fixture.</div>;
  }
  const slot = (view.width - 64) / view.selected.length;

  return <div className="chart-shell">
    <div className="chart-tools">
      <label className="toggle-label"><input type="checkbox" checked={showZones}
        onChange={(event) => setShowZones(event.target.checked)} /> Zones</label>
      <label className="toggle-label"><input type="checkbox" checked={showLevels}
        onChange={(event) => setShowLevels(event.target.checked)} /> Unswept levels</label>
      <span>Latest {view.selected.length} completed candles</span>
    </div>
    <div className="chart-scroll" role="region" aria-label={`${timeframe} candlestick chart`} tabIndex={0}>
      <svg className="price-chart" width={view.width} height={view.height}
        viewBox={`0 0 ${view.width} ${view.height}`} role="img"
        aria-label={`Synthetic ${timeframe} candlestick chart with analytical overlays`}>
        {[0, 1, 2, 3].map((step) => {
          const y = view.top + step * view.chartHeight / 3;
          const value = view.max - step * (view.max - view.min) / 3;
          return <g key={step}><line x1="46" x2={view.width - 8} y1={y} y2={y} className="chart-grid" />
            <text x="4" y={y + 4} className="chart-axis">{value.toFixed(2)}</text></g>;
        })}
        {showZones && activeZones.map((zone) => <g key={zone.zone_id}>
          <rect x="48" y={view.y(zone.high)} width={view.width - 58}
            height={Math.max(2, view.y(zone.low) - view.y(zone.high))}
            className={`zone-band ${zone.side}`} />
          <text x={view.width - 130} y={view.y(zone.high) - 4} className="overlay-label">
            {zone.side} zone · {zone.state}</text>
        </g>)}
        {showLevels && visibleLevels.map((level) => <g key={level.level_id}>
          <line x1="48" x2={view.width - 8} y1={view.y(level.price)} y2={view.y(level.price)}
            className="level-line" />
          <text x="54" y={view.y(level.price) - 4} className="overlay-label">
            {level.kind.replaceAll("_", " ")} {level.price.toFixed(2)}</text>
        </g>)}
        {view.selected.map((candle, index) => {
          const x = 50 + index * slot + slot / 2;
          const rising = candle.close >= candle.open;
          const candleTop = view.y(Math.max(candle.open, candle.close));
          const candleBottom = view.y(Math.min(candle.open, candle.close));
          return <g key={candle.timestamp}>
            <line x1={x} x2={x} y1={view.y(candle.high)} y2={view.y(candle.low)}
              className={rising ? "candle-wick up" : "candle-wick down"} />
            <rect x={x - Math.max(2, slot * 0.27)} y={candleTop}
              width={Math.max(4, slot * 0.54)} height={Math.max(1.5, candleBottom - candleTop)}
              className={rising ? "candle-body up" : "candle-body down"} />
            {index === 0 || index === view.selected.length - 1 || index % Math.max(1, Math.floor(view.selected.length / 4)) === 0
              ? <text x={x} y={view.height - 8} textAnchor="middle" className="chart-axis">
                {new Date(candle.timestamp).toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit" })}
              </text> : null}
          </g>;
        })}
      </svg>
    </div>
    <p className="chart-caption">Candles and overlays are supplied by the synthetic fixture API. Chart position is a visual mapping only.</p>
  </div>;
}
