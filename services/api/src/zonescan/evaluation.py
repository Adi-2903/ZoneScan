"""Validation and deterministic, fixture-friendly historical replay evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .models import ReplayBar
from .replay import ReplayResult, replay

KOLKATA = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True, slots=True)
class DatasetProvenance:
    dataset_id: str
    source_name: str
    source_reference: str
    usage_permission_reference: str
    permitted_for_internal_evaluation: bool
    synthetic: bool = False


@dataclass(frozen=True, slots=True)
class HistoricalSession:
    session_date: date
    opens_at: datetime
    closes_at: datetime
    expected_instrument_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HistoricalDataset:
    provenance: DatasetProvenance
    instrument_symbols: tuple[tuple[str, str], ...]
    sessions: tuple[HistoricalSession, ...]
    bars: tuple[ReplayBar, ...]
    interval_minutes: int = 5


@dataclass(frozen=True, slots=True)
class DatasetValidation:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    missing_intervals: tuple[tuple[str, datetime], ...]
    missing_oi_count: int
    universe_coverage_complete: bool

    @property
    def valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True, slots=True)
class Metric:
    available: bool
    value: float | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class EvaluationObservation:
    instrument_id: str
    timestamp: datetime
    score_available: bool
    score: float | None
    components: dict[str, float | None]
    unavailable_reasons: dict[str, str]
    direction: str | None
    forward_return_30m: Metric
    forward_return_60m: Metric
    forward_return_session_close: Metric
    maximum_favorable_atr: Metric
    maximum_adverse_atr: Metric
    zone_touch_before_close: Metric


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    validation: DatasetValidation
    replay: ReplayResult
    observations: tuple[EvaluationObservation, ...]


def validate_dataset(dataset: HistoricalDataset) -> DatasetValidation:
    errors: list[str] = []
    warnings: list[str] = []
    missing_intervals: list[tuple[str, datetime]] = []
    if not dataset.provenance.dataset_id.strip() or not dataset.provenance.source_name.strip() or not dataset.provenance.source_reference.strip():
        errors.append("dataset_provenance_incomplete")
    if not dataset.provenance.usage_permission_reference.strip():
        errors.append("usage_permission_reference_missing")
    if not dataset.provenance.permitted_for_internal_evaluation:
        errors.append("dataset_not_permitted_for_internal_evaluation")
    if dataset.interval_minutes not in (5, 15):
        errors.append("unsupported_candle_interval")
    instruments = dict(dataset.instrument_symbols)
    if len(instruments) != len(dataset.instrument_symbols) or any(not key.strip() or not value.strip() for key, value in dataset.instrument_symbols):
        errors.append("instrument_mapping_invalid_or_duplicate")
    if len({s.session_date for s in dataset.sessions}) != len(dataset.sessions):
        errors.append("duplicate_session_date")
    sessions = {s.session_date: s for s in dataset.sessions}
    for session in dataset.sessions:
        if session.opens_at.tzinfo is None or session.closes_at.tzinfo is None:
            errors.append("session_timestamp_timezone_missing")
        elif session.opens_at.astimezone(KOLKATA).date() != session.session_date or session.closes_at.astimezone(KOLKATA).date() != session.session_date or session.closes_at <= session.opens_at:
            errors.append("session_timestamp_invalid")
        if len(set(session.expected_instrument_ids)) != len(session.expected_instrument_ids):
            errors.append("duplicate_expected_instrument")
        if any(item not in instruments for item in session.expected_instrument_ids):
            errors.append("expected_instrument_mapping_missing")

    seen: set[tuple[str, str, datetime]] = set()
    previous: dict[tuple[str, str], ReplayBar] = {}
    observed: dict[tuple[date, str], set[datetime]] = {}
    missing_oi = 0
    universe_complete = bool(dataset.sessions)
    previous_global: datetime | None = None
    for bar in dataset.bars:
        c = bar.candle
        if c.timestamp.tzinfo is None or c.timestamp.utcoffset() is None:
            errors.append("candle_timestamp_timezone_missing")
            continue
        if c.instrument_id not in instruments:
            errors.append("instrument_mapping_missing")
        if c.timestamp.utcoffset() != timedelta(hours=5, minutes=30):
            errors.append("candle_timezone_must_be_utc_plus_0530")
        identity = (c.instrument_id, bar.timeframe, c.timestamp)
        if identity in seen:
            errors.append("duplicate_candle")
        seen.add(identity)
        if previous_global is not None and c.timestamp < previous_global:
            errors.append("dataset_timestamp_ordering_invalid")
        previous_global = c.timestamp
        stream = (c.instrument_id, bar.timeframe)
        old = previous.get(stream)
        if old and c.timestamp <= old.candle.timestamp:
            errors.append("candle_ordering_invalid")
        previous[stream] = bar
        if c.low <= 0 or c.high < c.low or not c.low <= c.open <= c.high or not c.low <= c.close <= c.high or c.volume < 0:
            errors.append("ohlc_or_volume_invalid")
        if c.volume is None:
            errors.append("volume_missing")
        if bar.oi_change_daily_pct is None:
            missing_oi += 1
        local_date = c.timestamp.astimezone(KOLKATA).date()
        session = sessions.get(bar.session_date or local_date)
        if session is None:
            errors.append("candle_session_missing")
            continue
        if local_date != session.session_date or not session.opens_at < c.timestamp <= session.closes_at:
            errors.append("candle_outside_session")
        elif (c.timestamp - session.opens_at).total_seconds() % (dataset.interval_minutes * 60):
            errors.append("candle_timestamp_not_interval_aligned")
        observed.setdefault((session.session_date, c.instrument_id), set()).add(c.timestamp)

    for session in dataset.sessions:
        if (session.closes_at - session.opens_at).total_seconds() % (dataset.interval_minutes * 60):
            errors.append("session_duration_not_interval_aligned")
        expected = tuple(session.opens_at + timedelta(minutes=dataset.interval_minutes * i)
                         for i in range(1, int((session.closes_at - session.opens_at).total_seconds() // (dataset.interval_minutes * 60)) + 1))
        for instrument in session.expected_instrument_ids:
            actual = observed.get((session.session_date, instrument), set())
            for timestamp in expected:
                if timestamp not in actual:
                    missing_intervals.append((instrument, timestamp))
            if any(timestamp not in actual for timestamp in expected):
                universe_complete = False
    if missing_intervals:
        warnings.append("missing_candle_intervals")
    if missing_oi:
        warnings.append("oi_missing_for_some_bars")
    if not universe_complete:
        warnings.append("point_in_time_universe_coverage_incomplete")
    return DatasetValidation(tuple(dict.fromkeys(errors)), tuple(dict.fromkeys(warnings)),
                             tuple(missing_intervals), missing_oi, universe_complete)


def _unavailable(reason: str) -> Metric:
    return Metric(False, reason=reason)


def _metric(value: float | None, reason: str) -> Metric:
    return Metric(True, value=value) if value is not None else _unavailable(reason)


def evaluate(dataset: HistoricalDataset) -> EvaluationResult:
    validation = validate_dataset(dataset)
    if not validation.valid:
        raise ValueError("invalid historical dataset: " + ",".join(validation.errors))
    bars = tuple(sorted(dataset.bars, key=lambda b: (b.candle.timestamp, b.candle.instrument_id, b.timeframe)))
    replay_result = replay(bars)
    index = {(b.candle.instrument_id, b.candle.timestamp): (i, b) for i, b in enumerate(bars)}
    scores = {(s.instrument_id, s.timestamp): s for s in replay_result.scores}
    created = [e for e in replay_result.events if e.kind == "zone_created" and e.zone_id]
    observations: list[EvaluationObservation] = []
    for (instrument, timestamp), (i, bar) in index.items():
        score_record = scores[(instrument, timestamp)]
        session = next((s for s in dataset.sessions if s.session_date == (bar.session_date or timestamp.astimezone(KOLKATA).date())), None)
        same_session = [(j, future) for j, future in enumerate(bars) if future.candle.instrument_id == instrument and future.timeframe == bar.timeframe and future.candle.timestamp > timestamp and session and future.candle.timestamp <= session.closes_at]
        complete = [future for _, future in same_session]
        def forward(minutes: int) -> Metric:
            target = timestamp + timedelta(minutes=minutes)
            hit = next((f for f in complete if f.candle.timestamp == target), None)
            if hit is None or not hit.candle.complete:
                return _unavailable("future_candle_missing_or_session_incomplete")
            return Metric(True, (hit.candle.close / bar.candle.close) - 1.0)
        close_bar = next((f for f in complete if session and f.candle.timestamp == session.closes_at and f.candle.complete), None)
        # Synthetic fixtures may exercise mechanics, but never expose performance metrics.
        synthetic = dataset.provenance.synthetic
        direction = score_record.direction
        completed_future = [f for f in complete if f.candle.complete]
        if not synthetic and direction in ("bullish", "bearish") and bar.atr is not None and completed_future:
            highs = [f.candle.high for f in completed_future]
            lows = [f.candle.low for f in completed_future]
            if direction == "bullish":
                mfe, mae = (max(highs) - bar.candle.close) / bar.atr, (bar.candle.close - min(lows)) / bar.atr
            else:
                mfe, mae = (bar.candle.close - min(lows)) / bar.atr, (max(highs) - bar.candle.close) / bar.atr
            mfe_metric, mae_metric = Metric(True, mfe), Metric(True, mae)
        elif bar.atr is None:
            mfe_metric = mae_metric = _unavailable("atr_missing")
        elif direction not in ("bullish", "bearish"):
            mfe_metric = mae_metric = _unavailable("scored_direction_unavailable")
        else:
            mfe_metric = mae_metric = _unavailable("synthetic_dataset_not_performance_eligible")
        zone_metric = _unavailable("no_order_block_created_at_timestamp")
        # Label only an order block emitted at this decision timestamp. A touch is
        # a later lifecycle state; no touch is false only after a complete session.
        created_here = [e.zone_id for e in created if e.timestamp == timestamp and
                        next((z for z in replay_result.zones if z.zone_id == e.zone_id), None) is not None]
        if not synthetic and created_here:
            touched = any(event.zone_id in created_here and event.timestamp > timestamp and
                          event.timestamp <= (session.closes_at if session else timestamp) and
                          ((event.kind == "zone_state_changed" and event.state in ("tested", "mitigated")) or event.kind == "zone_touched")
                          for event in replay_result.events)
            if touched:
                zone_metric = Metric(True, 1.0)
            elif session and timestamp <= session.closes_at and not any(
                    instrument in session.expected_instrument_ids and
                    session.opens_at < missing_at <= session.closes_at
                    for instrument, missing_at in validation.missing_intervals) and any(
                    f.candle.instrument_id == instrument and f.candle.timestamp == session.closes_at and f.candle.complete
                    for instrument in session.expected_instrument_ids for f in bars):
                zone_metric = Metric(True, 0.0)
            else:
                zone_metric = _unavailable("session_incomplete_for_zone_touch")
        elif synthetic:
            zone_metric = _unavailable("synthetic_dataset_not_performance_eligible")
        observations.append(EvaluationObservation(
            instrument, timestamp, score_record.result.available,
            score_record.result.strength, score_record.result.components,
            score_record.result.component_reasons or {}, direction,
            _unavailable("synthetic_dataset_not_performance_eligible") if synthetic else forward(30),
            _unavailable("synthetic_dataset_not_performance_eligible") if synthetic else forward(60),
            _unavailable("synthetic_dataset_not_performance_eligible") if synthetic else _metric((close_bar.candle.close / bar.candle.close) - 1 if close_bar else None, "session_close_candle_missing_or_incomplete"),
            mfe_metric, mae_metric, zone_metric))
    return EvaluationResult(validation, replay_result, tuple(observations))
