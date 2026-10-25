"""Read-only orchestration over the shared analytical pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from . import ALGORITHM_VERSION, PARAMETER_VERSION
from .indicators import aggregate_candles, calculate_indicators, to_replay_bars
from .models import BoardRow, BoardSnapshot, ReplayBar, ReplayScore, Zone
from .replay import ReplayResult, replay
from .synthetic_analytics import (SyntheticAnalyticsDataset,
                                  build_synthetic_analytics_dataset)


@dataclass(frozen=True, slots=True)
class AnalyticsSnapshot:
    as_of: datetime
    data_as_of: datetime
    data_source: str
    data_mode: str
    data_status: str
    market_state: str
    settling: bool
    settling_reason: str
    universe_expected: int
    universe_eligible: int
    symbols_excluded: int
    exclusion_summary: dict[str, int]
    replay: ReplayResult
    bars: tuple[ReplayBar, ...]
    board: BoardSnapshot


class AnalyticsService:
    """Build one immutable fixture snapshot at construction, then serve reads."""

    def __init__(self, dataset: SyntheticAnalyticsDataset | None = None) -> None:
        self.dataset = dataset or build_synthetic_analytics_dataset()
        instrument_symbols = {item.instrument_id: item.symbol
                             for item in self.dataset.instruments}
        aggregated = aggregate_candles(self.dataset.one_minute_candles,
                                       self.dataset.sessions, "5m")
        frames = calculate_indicators(
            aggregated, self.dataset.sessions, self.dataset.daily_candles,
            self.dataset.open_interest, self.dataset.contract_mappings)
        bars = tuple(to_replay_bars(frames, self.dataset.sector_directions))
        bars = tuple(ReplayBar(
            candle=bar.candle, atr=bar.atr, rvol=bar.rvol, timeframe=bar.timeframe,
            session_date=bar.session_date, day_return=bar.day_return,
            daily_sigma20=bar.daily_sigma20,
            oi_change_daily_pct=bar.oi_change_daily_pct,
            price_above_vwap=bar.price_above_vwap,
            price_above_ema20=bar.price_above_ema20,
            sector_direction=bar.sector_direction, adx14=bar.adx14,
            indicator_unavailable_reasons=bar.indicator_unavailable_reasons,
            symbol=instrument_symbols[bar.candle.instrument_id],
            oi_change_30m_pct=bar.oi_change_30m_pct,
        ) for bar in bars)
        result = replay(bars, trading_sessions=self.dataset.sessions)
        if not result.boards:
            raise RuntimeError("synthetic analytical fixture produced no board snapshot")
        final_board = result.boards[-1]
        current_scores = [score for score in result.scores
                          if score.timestamp == final_board.timestamp]
        eligible = {score.instrument_id for score in current_scores
                    if score.result.available and score.choppy is not None
                    and score.choppy.available and score.choppy.is_choppy is False
                    and score.filtered_strength is not None}
        excluded = max(0, len(self.dataset.instruments) - len(eligible))
        self.snapshot = AnalyticsSnapshot(
            as_of=final_board.timestamp,
            data_as_of=final_board.timestamp,
            data_source=self.dataset.source,
            data_mode="synthetic",
            data_status="synthetic",
            market_state="unknown",
            settling=False,
            settling_reason="not_applicable_fixed_synthetic_fixture",
            universe_expected=len(self.dataset.instruments),
            universe_eligible=len(eligible),
            symbols_excluded=excluded,
            exclusion_summary={"ineligible_or_unavailable": excluded},
            replay=result,
            bars=bars,
            board=final_board,
        )
        self._symbols = {item.symbol.upper(): item.instrument_id
                         for item in self.dataset.instruments}
        self._instrument_by_id = {item.instrument_id: item for item in self.dataset.instruments}
        self._bar_by_key = {(bar.candle.instrument_id, bar.timeframe, bar.candle.timestamp): bar
                            for bar in bars}
        self._score_by_key = {(score.instrument_id, score.timestamp): score
                              for score in result.scores}

    def instrument_id_for_symbol(self, symbol: str) -> str | None:
        return self._symbols.get(symbol.upper())

    def instrument(self, instrument_id: str):
        return self._instrument_by_id[instrument_id]

    def latest_score(self, instrument_id: str) -> ReplayScore | None:
        return self._score_by_key.get((instrument_id, self.snapshot.as_of))

    def latest_bar(self, instrument_id: str) -> ReplayBar | None:
        return self._bar_by_key.get((instrument_id, "5m", self.snapshot.as_of))

    def board_rows(self, side: str) -> tuple[BoardRow, ...]:
        return self.snapshot.board.bullish if side == "bull" else self.snapshot.board.bearish

    def zones_for(self, instrument_id: str) -> tuple[Zone, ...]:
        return tuple(sorted((zone for zone in self.snapshot.replay.zones
                            if zone.instrument_id == instrument_id
                            and zone.recognized_at <= self.snapshot.as_of),
                            key=lambda zone: (zone.recognized_at, zone.zone_id)))

    def liquidity_for(self, instrument_id: str):
        return tuple(sorted((level for level in self.snapshot.replay.liquidity_levels
                            if level.instrument_id == instrument_id
                            and level.confirmed_at <= self.snapshot.as_of),
                            key=lambda level: (level.confirmed_at, level.level_id)))


def versions() -> dict[str, str]:
    return {"algorithm_version": ALGORITHM_VERSION,
            "parameter_version": PARAMETER_VERSION}
