from __future__ import annotations

from collections import defaultdict
from math import isfinite

from .models import BoardRow, BoardSnapshot, ReplayScore


BOARD_LIMIT = 20
NEW_ENTRY_MARGIN = 2.0
INCUMBENT_EXIT_MARGIN = 3.0
SMOOTH_CURRENT_WEIGHT = 0.6
SMOOTH_PREVIOUS_WEIGHT = 0.4


def smooth_score(current_score: float | None,
                 previous_smoothed_score: float | None) -> float | None:
    """Return a smoothed score, or None when the current score is unavailable."""
    if current_score is None or not isfinite(current_score):
        return None
    if previous_smoothed_score is None:
        return current_score
    if not isfinite(previous_smoothed_score):
        return None
    return (SMOOTH_CURRENT_WEIGHT * current_score
            + SMOOTH_PREVIOUS_WEIGHT * previous_smoothed_score)


def _eligible(score: ReplayScore, side: str) -> bool:
    return (
        score.result.available
        and score.direction == side
        and score.choppy is not None
        and score.choppy.available
        and score.choppy.is_choppy is False
        and score.result.strength is not None
        and isfinite(score.result.strength)
        and score.filtered_strength is not None
        and isfinite(score.filtered_strength)
        and score.smoothed_strength is not None
        and score.rvol is not None
        and score.traded_value is not None
        and isfinite(score.smoothed_strength)
        and isfinite(score.rvol)
        and isfinite(score.traded_value)
        and score.rvol >= 0
        and score.traded_value >= 0
    )


def _sort_key(score: ReplayScore, symbols: dict[str, str]) -> tuple[float, float, float, str]:
    return (-score.smoothed_strength, -score.rvol, -score.traded_value,
            symbols[score.instrument_id])


def _rank_side(scores: tuple[ReplayScore, ...], side: str,
               previous_rows: tuple[BoardRow, ...],
               symbols: dict[str, str], limit: int) -> tuple[BoardRow, ...]:
    candidates = [score for score in scores if _eligible(score, side)]
    candidates.sort(key=lambda score: _sort_key(score, symbols))
    prior_ids = {row.instrument_id for row in previous_rows}
    prior_cutoff = (previous_rows[-1].score.smoothed_strength
                    if len(previous_rows) == limit else None)

    if prior_cutoff is None:
        selected = candidates[:limit]
    else:
        retained = [score for score in candidates
                    if score.instrument_id in prior_ids
                    and score.smoothed_strength >= prior_cutoff - INCUMBENT_EXIT_MARGIN]
        entrants = [score for score in candidates
                    if score.instrument_id not in prior_ids
                    and score.smoothed_strength >= prior_cutoff + NEW_ENTRY_MARGIN]
        retained.sort(key=lambda score: _sort_key(score, symbols))
        entrants.sort(key=lambda score: _sort_key(score, symbols))
        selected = retained + entrants
        selected.sort(key=lambda score: _sort_key(score, symbols))
        selected = selected[:limit]

    return tuple(BoardRow(rank=index, instrument_id=score.instrument_id,
                          symbol=symbols[score.instrument_id], side=side, score=score)
                 for index, score in enumerate(selected, start=1))


def build_board_snapshots(scores: tuple[ReplayScore, ...] | list[ReplayScore],
                          symbols: dict[str, str]) -> tuple[BoardSnapshot, ...]:
    """Build chronological per-timestamp boards using only that timestamp's scores."""
    grouped: dict[tuple[object, object], list[ReplayScore]] = defaultdict(list)
    for score in scores:
        if score.session_date is None or score.timeframe != "5m":
            continue
        grouped[(score.timestamp, score.session_date)].append(score)

    previous: dict[tuple[object, str], tuple[BoardRow, ...]] = {}
    snapshots: list[BoardSnapshot] = []
    for timestamp, session_date in sorted(grouped):
        point_scores = tuple(sorted(grouped[(timestamp, session_date)],
                                    key=lambda score: score.instrument_id))
        point_symbols = {score.instrument_id: symbols.get(score.instrument_id,
                                                           score.instrument_id)
                         for score in point_scores}
        board_rows: dict[str, tuple[BoardRow, ...]] = {}
        for side in ("bullish", "bearish"):
            key = (session_date, side)
            board_rows[side] = _rank_side(point_scores, side,
                                          previous.get(key, ()), point_symbols,
                                          BOARD_LIMIT)
            previous[key] = board_rows[side]
        snapshots.append(BoardSnapshot(timestamp, session_date,
                                        board_rows["bullish"], board_rows["bearish"]))
    return tuple(snapshots)
