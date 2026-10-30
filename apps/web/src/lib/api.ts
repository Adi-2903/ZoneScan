export type ApiMeta = {
  as_of: string;
  data_as_of: string;
  data_source: string;
  data_mode: string;
  data_status: string;
  market_state: string;
  settling: boolean;
  algorithm_version: string;
  parameter_version: string;
};

export type BoardResponse = ApiMeta & {
  side: "bull" | "bear";
  rows: BoardRow[];
};

export type BoardRow = {
  rank: number;
  symbol: string;
  price: number | null;
  change_pct: number | null;
  strength: number | null;
  filtered_strength: number | null;
  smoothed_strength: number | null;
  early_move: EarlyMove | null;
  score_breakdown: Score;
  sector: string | null;
  sector_badge: string;
  zone: { available?: boolean; reason?: string; state?: string; low?: number; high?: number };
  levels: LiquidityLevel[];
  trend: string | null;
  quality_flags: string[];
};

export type MarketStatus = ApiMeta & {
  session_open_at: string | null;
  session_close_at: string | null;
  settling_reason: string | null;
  universe_expected: number;
  universe_eligible: number;
  symbols_excluded: number;
  exclusion_summary: Record<string, number>;
};

export type Score = {
  available: boolean;
  strength: number | null;
  components: Record<string, number | null>;
  component_reasons: Record<string, string>;
  component_contexts: Record<string, string>;
  unavailable_reason: string | null;
  direction: string | null;
  filtered_strength: number | null;
  smoothed_strength: number | null;
  choppy?: { available: boolean; is_choppy: boolean | null; reason: string | null } | null;
  early_move?: EarlyMove | null;
};

export type EarlyMove = {
  available: boolean;
  score: number | null;
  components: Record<string, number | null>;
  component_reasons: Record<string, string>;
  reason: string | null;
};

export type Indicator = { available: boolean; value: number | boolean | null; reason: string | null };
export type Zone = {
  zone_id: string;
  side: string;
  low: number;
  high: number;
  timeframe: string;
  formed_at: string;
  recognized_at: string;
  state: string;
  active: boolean;
};
export type LiquidityLevel = {
  level_id: string;
  kind: string;
  side: string;
  price: number;
  timeframe: string;
  state: string;
  formed_at: string;
  confirmed_at: string;
  swept_at: string | null;
  unavailable_reason: string | null;
};

export type StockResponse = ApiMeta & {
  symbol: string;
  instrument_id: string;
  price: number | null;
  quality_flags: string[];
  sector: string | null;
  indicators: Record<string, Indicator> | { available: false; reason: string };
  strength: Score;
  zones: Zone[];
  liquidity_levels: LiquidityLevel[];
};

export type Candle = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  complete: boolean;
  quality_flags: string[];
};

export type CandleResponse = ApiMeta & {
  symbol: string;
  timeframe: string;
  candles: Candle[];
};

export type XRayClassification = "bullish" | "bearish" | "choppy" | "neutral" | "unavailable";
export type XRayInstrument = {
  symbol: string;
  instrument_id: string;
  direction: string | null;
  change_pct: number | null;
  classification: XRayClassification;
  classification_available: boolean;
  unavailable_reason: string | null;
  timestamp: string | null;
};
export type XRayResponse = ApiMeta & {
  instruments: XRayInstrument[];
  counts: Record<XRayClassification, number>;
  leaders: XRayInstrument[];
  laggards: XRayInstrument[];
  coverage: { covered_instruments: number; universe_complete: false; scope: string; label: string; unavailable_values: number };
};

type ErrorEnvelope = { error?: { code?: string; message?: string; request_id?: string } };

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { cache: "no-store", signal });
  } catch (cause) {
    if (cause instanceof Error && cause.name === "AbortError") throw cause;
    throw new Error(`Cannot reach the ZoneScan API at ${API_BASE}. Start the backend and retry.`);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as ErrorEnvelope;
    const error = body.error;
    throw new Error(error?.request_id
      ? `${error.message ?? "Request failed."} (request ${error.request_id})`
      : error?.message ?? `Request failed with status ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  status: (signal?: AbortSignal) => getJson<MarketStatus>("/api/v1/market/status", signal),
  board: (side: "bull" | "bear", signal?: AbortSignal) => getJson<BoardResponse>(`/api/v1/board?side=${side}`, signal),
  stock: (symbol: string, signal?: AbortSignal) => getJson<StockResponse>(`/api/v1/stocks/${encodeURIComponent(symbol)}`, signal),
  candles: (symbol: string, timeframe: string, signal?: AbortSignal) => getJson<CandleResponse>(
    `/api/v1/stocks/${encodeURIComponent(symbol)}/candles?tf=${encodeURIComponent(timeframe)}`, signal),
  xray: (signal?: AbortSignal) => getJson<XRayResponse>("/api/v1/xray", signal),
};

export function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata", dateStyle: "medium", timeStyle: "short",
  }).format(parsed) + " IST";
}

export function formatPrice(value: number | null): string {
  return value === null ? "Unavailable" : value.toFixed(2);
}

export function formatPercent(value: number | null): string {
  return value === null ? "Unavailable" : `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}
