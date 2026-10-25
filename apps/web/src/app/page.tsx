"use client";

import { useCallback, useEffect, useState } from "react";
import { api, formatPercent, formatPrice, formatTimestamp } from "@/lib/api";
import type { BoardResponse, BoardRow, CandleResponse, MarketStatus, StockResponse } from "@/lib/api";
import { ZoneChart } from "@/components/ZoneChart";

type Side = "bull" | "bear";
type View = "board" | "stock";

const componentNames: Record<string, string> = {
  M: "Move", V: "Volume", O: "Open interest", T: "Trend", S: "Sector", Z: "Zone",
};

export default function Dashboard() {
  const [side, setSide] = useState<Side>("bull");
  const [view, setView] = useState<View>("board");
  const [status, setStatus] = useState<MarketStatus | null>(null);
  const [board, setBoard] = useState<BoardResponse | null>(null);
  const [stock, setStock] = useState<StockResponse | null>(null);
  const [candles, setCandles] = useState<CandleResponse | null>(null);
  const [timeframe, setTimeframe] = useState("5m");
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [detailRefresh, setDetailRefresh] = useState(0);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [lightTheme, setLightTheme] = useState(false);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    try {
      const [nextStatus, nextBoard] = await Promise.all([api.status(signal), api.board(side, signal)]);
      setStatus(nextStatus);
      setBoard(nextBoard);
    } catch (cause) {
      if (!signal?.aborted) setError(cause instanceof Error ? cause.message : "Unable to load market data.");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [side]);

  useEffect(() => {
    const controller = new AbortController();
    void Promise.resolve().then(() => refresh(controller.signal));
    return () => controller.abort();
  }, [refresh]);

  const openStock = useCallback((symbol: string) => {
    setStock(null);
    setCandles(null);
    setDetailError(null);
    setDetailLoading(true);
    setSelectedSymbol(symbol);
    setView("stock");
  }, []);

  useEffect(() => {
    if (view !== "stock" || !selectedSymbol) return;
    let active = true;
    Promise.all([api.stock(selectedSymbol), api.candles(selectedSymbol, timeframe)])
      .then(([detail, chart]) => {
        if (active) { setStock(detail); setCandles(chart); setDetailError(null); }
      })
      .catch((cause: unknown) => {
        if (active) setDetailError(cause instanceof Error ? cause.message : "Unable to load chart data.");
      })
      .finally(() => { if (active) setDetailLoading(false); });
    return () => { active = false; };
  }, [view, selectedSymbol, timeframe, detailRefresh]);

  const rows = board?.side === side ? board.rows : [];
  const boardLoading = loading || (!error && board?.side !== side);
  const meta = stock ?? board ?? status;

  return <main className={lightTheme ? "app light" : "app"}>
    <div className="demo-ribbon"><span className="demo-dot" /> SYNTHETIC FIXTURE · NOT LIVE MARKET DATA</div>
    <div className="app-frame">
      <aside className="sidebar">
        <a className="brand" href="#board" onClick={(event) => { event.preventDefault(); setView("board"); }}>
          <span className="brand-mark">Z</span><span>ZoneScan<small>MARKET INTELLIGENCE</small></span>
        </a>
        <div className="sidebar-label">WORKSPACE</div>
        <button className={`nav-item ${view === "board" ? "active" : ""}`} onClick={() => setView("board")}>
          <span>▦</span> Market board
        </button>
        <button className="nav-item muted-nav" disabled title="Not part of this prototype"><span>⌕</span> Market X-Ray</button>
        <div className="sidebar-bottom">
          <div className="source-card"><span className="status-lamp" />Fixture engine
            <small>Fixed historical sample</small></div>
          <button className="theme-button" onClick={() => setLightTheme((value) => !value)}>
            {lightTheme ? "☾  Dark appearance" : "☼  Light appearance"}
          </button>
          <p className="sidebar-foot">Analytics prototype<br />No trade execution</p>
        </div>
      </aside>

      <section className="main-column">
        <header className="topbar">
          <div className="mobile-brand"><span className="brand-mark">Z</span><strong>ZoneScan</strong></div>
          <div className="breadcrumbs"><span>Workspace</span><b>/</b><strong>{view === "board" ? "Market board" : `${selectedSymbol ?? "Stock"} detail`}</strong></div>
          <div className="topbar-actions">
            <span className="market-unknown"><i /> {status?.market_state === "closed" ? "Market closed" : "Session status unavailable"}</span>
            <button className="icon-button" aria-label="Toggle theme" onClick={() => setLightTheme((value) => !value)}>{lightTheme ? "☾" : "☼"}</button>
          </div>
        </header>

        <div className="page-content">
          <div className="mobile-synthetic">Synthetic fixture data · not live</div>
          <div className="page-heading">
            <div>
              {view === "stock" && <button className="back-link" onClick={() => setView("board")}>← Back to board</button>}
              <p className="eyebrow">{view === "board" ? "MARKET OVERVIEW" : "INSTRUMENT ANALYSIS"}</p>
              <h1>{view === "board" ? "Market board" : stock?.symbol ?? selectedSymbol ?? "Stock detail"}</h1>
              <p className="subheading">{view === "board" ? "Ranked synthetic examples from the deterministic replay fixture." : "Point-in-time analytics and completed candle context."}</p>
            </div>
            <div className="heading-actions">
              {view === "board" ? <button className="refresh-button" onClick={() => { setError(null); setLoading(true); void refresh(); }} disabled={loading}>↻ <span>Refresh</span></button>
                : <span className="asof-pill">Snapshot · {meta ? formatTimestamp(meta.as_of) : "—"}</span>}
            </div>
          </div>

          <section className="status-strip" aria-label="Data status">
            <div className="status-icon">◎</div>
            <div className="status-main"><strong>DEMO DATA · SYNTHETIC</strong>
              <span>Fixed fixture snapshot. No live prices, provider feed, or current-session status.</span></div>
            <div className="status-asof"><small>DATA AS OF</small><strong>{meta ? formatTimestamp(meta.data_as_of) : "Awaiting API"}</strong></div>
          </section>

          {view === "board" ? <>
            {error && <div className="error-state" role="alert"><div><strong>API unavailable</strong><p>{error}</p></div><button onClick={() => void refresh()}>Retry</button></div>}
            <div className="board-heading-row">
              <div className="tabs" role="tablist" aria-label="Board direction">
                <button role="tab" aria-selected={side === "bull"} className={side === "bull" ? "selected bull-tab" : ""}
                  onClick={() => { setError(null); setLoading(true); setSide("bull"); }}>↗ Bullish <span>{side === "bull" ? rows.length : ""}</span></button>
                <button role="tab" aria-selected={side === "bear"} className={side === "bear" ? "selected bear-tab" : ""}
                  onClick={() => { setError(null); setLoading(true); setSide("bear"); }}>↘ Bearish <span>{side === "bear" ? rows.length : ""}</span></button>
              </div>
              <div className="board-snapshot">{board ? `Snapshot · ${formatTimestamp(board.as_of)}` : "Snapshot · —"}</div>
            </div>
            <BoardTable rows={rows} loading={boardLoading} side={side} onSelect={openStock} />
            <div className="board-footnote"><span>ⓘ</span> Scores are deterministic heuristics from fixture inputs. They do not indicate certainty or profitability.</div>
          </> : <StockDetail symbol={selectedSymbol} stock={stock} candles={candles}
            timeframe={timeframe} setTimeframe={(value) => { setCandles(null); setDetailLoading(true); setTimeframe(value); }} loading={detailLoading}
            error={detailError} retry={() => { setStock(null); setCandles(null); setDetailLoading(true); setDetailRefresh((value) => value + 1); }} />}

          <footer className="footer"><span>ZoneScan · local prototype</span><span>Algorithm {meta?.algorithm_version ?? "—"} · Parameters {meta?.parameter_version ?? "—"}</span></footer>
        </div>
      </section>
    </div>
  </main>;
}

function BoardTable({ rows, loading, side, onSelect }: {
  rows: BoardRow[]; loading: boolean; side: Side; onSelect: (symbol: string) => void;
}) {
  if (loading && !rows.length) return <div className="table-card"><div className="loading-state"><span className="spinner" /> Loading fixture-backed board…</div>
    <div className="skeleton-rows">{[0, 1].map((item) => <div className="skeleton-row" key={item} />)}</div></div>;
  if (!loading && !rows.length) return <div className="table-card empty-state"><span className="empty-icon">⌁</span>
    <h2>No {side === "bull" ? "bullish" : "bearish"} rows available</h2><p>The API returned an empty board for this side.</p></div>;
  return <div className="table-card">
    <div className="table-title"><div><strong>{side === "bull" ? "Bullish" : "Bearish"} watchlist</strong><span>{rows.length} synthetic instrument{rows.length === 1 ? "" : "s"}</span></div>
      <span className="table-columns-note">Sorted by backend rank</span></div>
    <div className="desktop-table-wrap"><table className="board-table">
      <thead><tr><th>RANK</th><th>INSTRUMENT</th><th className="numeric">LAST PRICE</th><th className="numeric">CHANGE</th><th className="numeric">STRENGTH</th><th>SECTOR</th><th>DIRECTION</th></tr></thead>
      <tbody>{rows.map((row) => <tr key={row.symbol}>
        <td><span className="rank-number">{String(row.rank).padStart(2, "0")}</span></td>
        <td><button className="symbol-button" onClick={() => onSelect(row.symbol)}><span className="symbol-monogram">{row.symbol.slice(0, 1)}</span><span>{row.symbol}<small>{row.score_breakdown.available ? "Score available" : "Score unavailable"}</small></span><span className="row-arrow">↗</span></button></td>
        <td className="numeric price-cell">{formatPrice(row.price)}</td>
        <td className={`numeric ${row.change_pct === null ? "" : row.change_pct >= 0 ? "up-text" : "down-text"}`}>{formatPercent(row.change_pct)}</td>
        <td className="numeric">{row.strength === null ? <span className="unavailable-chip">Unavailable</span> : <span className="score-value">{row.strength.toFixed(1)}<small>/100</small></span>}</td>
        <td><span className="sector-cell">{row.sector ?? <span className="muted">Unavailable</span>}<small>{row.sector ? "Fixture input" : "Not supplied"}</small></span></td>
        <td><span className={`direction-pill ${row.trend === "bullish" ? "positive" : "negative"}`}>{row.trend === "bullish" ? "↗ Bullish" : row.trend === "bearish" ? "↘ Bearish" : "Unavailable"}</span></td>
      </tr>)}</tbody>
    </table></div>
    <div className="mobile-stock-list">{rows.map((row) => <button className="mobile-stock-row" key={row.symbol} onClick={() => onSelect(row.symbol)}>
      <span className="rank-number">{String(row.rank).padStart(2, "0")}</span><span className="mobile-symbol"><strong>{row.symbol}</strong><small>{row.sector ?? "Sector unavailable"}</small></span>
      <span className="mobile-numbers"><strong>{formatPrice(row.price)}</strong><small className={row.change_pct === null ? "muted" : row.change_pct >= 0 ? "up-text" : "down-text"}>{formatPercent(row.change_pct)}</small></span>
      <span className="mobile-score">{row.strength === null ? "—" : row.strength.toFixed(1)}<small>Strength</small></span>
    </button>)}</div>
    <div className="table-bottom"><span>Source: deterministic synthetic fixture</span><span>Click a row for analysis&nbsp; →</span></div>
  </div>;
}

function StockDetail({ symbol, stock, candles, timeframe, setTimeframe, loading, error, retry }: {
  symbol: string | null; stock: StockResponse | null; candles: CandleResponse | null;
  timeframe: string; setTimeframe: (value: string) => void; loading: boolean;
  error: string | null; retry: () => void;
}) {
  if (loading && !stock) return <div className="detail-card loading-state"><span className="spinner" /> Loading analytical detail…</div>;
  if (error) return <div className="error-state" role="alert"><div><strong>Could not load {symbol ?? "stock"}</strong><p>{error}</p></div><button onClick={retry}>Retry</button></div>;
  if (!stock) return <div className="empty-state"><h2>Detail unavailable</h2><p>No stock response was returned.</p></div>;
  const early = stock.strength.early_move;
  const activeZones = stock.zones.filter((zone) => zone.active && ["fresh", "tested"].includes(zone.state));
  const openLevels = stock.liquidity_levels.filter((level) => level.state === "unswept");

  return <div className="detail-layout">
    <section className="detail-card chart-card">
      <div className="detail-card-heading chart-heading"><div><p className="eyebrow">PRICE ACTION</p><h2>{stock.symbol} <span className="exchange-tag">NSE · SYNTHETIC</span></h2>
        <div className="detail-price">{formatPrice(stock.price)} <span className="neutral-caption">Snapshot close · {formatTimestamp(stock.as_of)}</span></div></div>
        <div className="timeframe-tabs" aria-label="Chart timeframe">{["1m", "5m", "15m", "1d"].map((tf) => <button key={tf} className={timeframe === tf ? "active" : ""} onClick={() => setTimeframe(tf)}>{tf}</button>)}</div>
      </div>
      {error && <div className="inline-error">{error}</div>}
      {loading && !candles ? <div className="empty-chart"><span className="spinner" /> Loading candle data…</div>
        : candles ? <ZoneChart candles={candles.candles} zones={stock.zones} levels={stock.liquidity_levels} timeframe={timeframe} />
        : <div className="empty-chart">Candle data unavailable for this timeframe.</div>}
    </section>

    <div className="detail-card-grid">
      <section className="detail-card score-card">
        <div className="detail-card-heading"><div><p className="eyebrow">CORE ANALYTICS</p><h2>Strength Score</h2></div><span className="version-mini">{stock.strength.available ? "AVAILABLE" : "UNAVAILABLE"}</span></div>
        {stock.strength.available && stock.strength.strength !== null
          ? <div className="score-hero"><strong>{stock.strength.strength.toFixed(1)}</strong><span>/ 100</span><span className={`direction-pill ${stock.strength.direction === "bullish" ? "positive" : "negative"}`}>{stock.strength.direction ?? "Direction unavailable"}</span></div>
          : <div className="unavailable-panel">Strength unavailable · {stock.strength.unavailable_reason ?? "Required inputs missing"}</div>}
        <div className="component-list">{Object.entries(stock.strength.components).map(([key, value]) => <div className="component-row" key={key}>
          <span><b>{key}</b>{componentNames[key] ?? key}</span><strong>{value === null ? "Unavailable" : value.toFixed(3)}</strong>
          {value === null && stock.strength.component_reasons[key] && <small>{stock.strength.component_reasons[key]}</small>}
        </div>)}</div>
        <div className="filtered-line"><span>Filtered / smoothed</span><strong>{stock.strength.filtered_strength?.toFixed(1) ?? "Unavailable"} / {stock.strength.smoothed_strength?.toFixed(1) ?? "Unavailable"}</strong></div>
      </section>

      <section className="detail-card early-card">
        <div className="detail-card-heading"><div><p className="eyebrow">MOMENTUM CONTEXT</p><h2>Early-Move Score</h2></div><span className="version-mini">PROVISIONAL</span></div>
        {early?.available && early.score !== null ? <div className="early-score-number">{early.score.toFixed(1)} <small>/ 100</small></div>
          : <div className="unavailable-panel">Unavailable · {early?.reason ?? "Required inputs missing"}</div>}
        <div className="component-list">{early && Object.entries(early.components).map(([key, value]) => <div className="component-row" key={key}>
          <span>{key}</span><strong>{value === null ? "Unavailable" : value.toFixed(3)}</strong>
          {value === null && early.component_reasons[key] && <small>{early.component_reasons[key]}</small>}
        </div>)}</div>
      </section>

      <section className="detail-card indicators-card">
        <div className="detail-card-heading"><div><p className="eyebrow">POINT-IN-TIME INPUTS</p><h2>Indicators</h2></div></div>
        <div className="indicator-grid">{Object.entries(stock.indicators).map(([key, input]) => {
          if (!input || typeof input !== "object" || !("available" in input)) return null;
          const { available, value, reason } = input;
          const percentMetric = ["day_return", "daily_sigma20", "oi_change_daily_pct", "oi_change_30m_pct"].includes(key);
          const formattedValue = typeof value === "number"
            ? percentMetric ? `${(value * 100).toFixed(2)}%` : key === "rvol" ? `${value.toFixed(2)}×` : value.toFixed(3)
            : typeof value === "boolean" ? value ? "Above" : "Below" : "Unavailable";
          return <div className="indicator-item" key={key}><span>{key.replaceAll("_", " ")}</span>
            <strong>{available && value !== null ? formattedValue : "Unavailable"}</strong>
            {!available && <small>{reason ?? "Input unavailable"}</small>}
          </div>;
        })}</div>
      </section>

      <section className="detail-card zones-card">
        <div className="detail-card-heading"><div><p className="eyebrow">STRUCTURE</p><h2>Order-block zones</h2></div><span className="count-pill">{activeZones.length} active</span></div>
        {stock.zones.length ? <div className="zone-list">{stock.zones.slice(-10).reverse().map((zone) => <div className="zone-row" key={zone.zone_id}>
          <span className={`zone-side ${zone.side}`}>{zone.side === "bullish" ? "↗ Bullish" : "↘ Bearish"}</span>
          <strong>{zone.low.toFixed(2)} – {zone.high.toFixed(2)}</strong>
          <span className={`lifecycle ${zone.state}`}>{zone.state}</span>
          <small>Recognized {formatTimestamp(zone.recognized_at)} · {zone.timeframe}</small>
        </div>)}</div> : <div className="empty-inline">No order-block zones are available in this snapshot.</div>}
      </section>

      <section className="detail-card levels-card">
        <div className="detail-card-heading"><div><p className="eyebrow">PRICE CONTEXT</p><h2>Liquidity levels</h2></div><span className="count-pill">{openLevels.length} unswept</span></div>
        {stock.liquidity_levels.length ? <div className="level-list">{stock.liquidity_levels.slice(-12).reverse().map((level) => <div className="level-row" key={level.level_id}>
          <span>{level.kind.replaceAll("_", " ")}</span><strong>{level.price.toFixed(2)}</strong><span className={`lifecycle ${level.state}`}>{level.state}</span>
          <small>{level.side} · confirmed {formatTimestamp(level.confirmed_at)}</small>
        </div>)}</div> : <div className="empty-inline">No liquidity levels are available in this snapshot.</div>}
      </section>
    </div>
    <p className="detail-disclaimer">Zones and scores are algorithmic analytics from synthetic fixture data. They do not identify actual institutional orders or provide trading instructions.</p>
  </div>;
}
