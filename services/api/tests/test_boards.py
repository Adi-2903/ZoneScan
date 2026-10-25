from dataclasses import replace
from datetime import date, datetime, timedelta
import unittest
from zoneinfo import ZoneInfo

from zonescan.boards import build_board_snapshots, smooth_score
from zonescan.models import (BoardSnapshot, ChoppyResult, ReplayScore, ScoreResult,
                             TradingSession)
from zonescan.replay import replay
from zonescan.scoring import classify_direction
from tests.test_replay_scoring import START, scoring_session

IST = ZoneInfo("Asia/Kolkata")
DAY = date(2026, 1, 5)


def candidate(instrument: int, timestamp: datetime, score: float,
              *, direction: str = "bullish", rvol: float = 1.0,
              traded_value: float = 1000.0, symbol: str | None = None,
              choppy: bool = False) -> ReplayScore:
    result = ScoreResult(True, score, {"M": .5, "V": .5, "O": .5,
                                      "T": .5, "S": .5, "Z": .5})
    chop = ChoppyResult(True, choppy, {}, {})
    return ReplayScore(f"I{instrument:02}", timestamp, result, direction, chop,
                       score, score, rvol, traded_value, DAY, "5m")


def snapshot(timestamp: datetime, rows: tuple[ReplayScore, ...],
             symbols: dict[str, str]) -> tuple[BoardSnapshot, ...]:
    return build_board_snapshots(rows, symbols)


class BoardEngineTests(unittest.TestCase):
    def test_direction_boundaries_and_unavailable_inputs(self):
        self.assertEqual("bullish", classify_direction(.001, "bullish", None))
        self.assertEqual("bullish", classify_direction(.001, "range", True))
        self.assertEqual("bearish", classify_direction(-.001, "bearish", None))
        self.assertEqual("bearish", classify_direction(-.001, "range", False))
        self.assertEqual("neutral", classify_direction(0, "bullish", True))
        self.assertEqual("neutral", classify_direction(.001, "bearish", True))
        self.assertIsNone(classify_direction(None, "bullish", True))
        self.assertIsNone(classify_direction(.001, None, True))
        self.assertIsNone(classify_direction(.001, "range", None))

    def test_smoothing_formula_first_value_missing_value_and_session_state_reset(self):
        self.assertEqual(80, smooth_score(80, None))
        self.assertEqual(72, smooth_score(60, 90))
        self.assertIsNone(smooth_score(None, 90))

        bars = scoring_session()
        bars = [replace(bar, symbol="SCORE-X", adx14=25)
                for bar in bars]
        for index in range(8):
            candle = replace(bars[-1].candle,
                             timestamp=bars[-1].candle.timestamp
                             + timedelta(minutes=5 * (index + 1)))
            bars.append(replace(bars[-1], candle=candle))
        first_calendar = TradingSession("SCORE-X", DAY,
                                        datetime.fromisoformat("2026-01-05T09:10:00+05:30"),
                                        bars[-1].candle.timestamp)
        first_session = replay(bars, trading_sessions=[first_calendar])
        adjacent_valid = [(prior, current)
                          for prior, current in zip(first_session.scores,
                                                    first_session.scores[1:])
                          if prior.smoothed_strength is not None
                          and current.filtered_strength is not None]
        for previous, current in adjacent_valid:
            self.assertAlmostEqual(.6 * current.filtered_strength
                                   + .4 * previous.smoothed_strength,
                                   current.smoothed_strength)

        next_day_bars = []
        next_start = datetime.fromisoformat("2026-01-06T09:15:00+05:30")
        for index, item in enumerate(bars):
            candle = replace(item.candle, timestamp=next_start + timedelta(minutes=5 * index))
            next_day_bars.append(replace(item, candle=candle, session_date=candle.timestamp.date()))
        second_calendar = TradingSession("SCORE-X", date(2026, 1, 6),
                                         datetime.fromisoformat("2026-01-06T09:10:00+05:30"),
                                         datetime.fromisoformat("2026-01-06T10:35:00+05:30"))
        reset_result = replay(next_day_bars, trading_sessions=[second_calendar])
        first_valid = next((score for score in reset_result.scores
                            if score.filtered_strength is not None), None)
        self.assertIsNotNone(first_valid)
        self.assertEqual(first_valid.filtered_strength, first_valid.smoothed_strength)

    def test_ranking_tiebreaks_top_twenty_and_choppy_exclusion(self):
        timestamp = START + timedelta(minutes=5)
        scores = [candidate(i, timestamp, 70, rvol=2, traded_value=1000,
                            symbol=f"SYM{i:02}") for i in range(25)]
        scores[0] = candidate(0, timestamp, 100, symbol="CHOP", choppy=True)
        scores[1] = candidate(1, timestamp, 70, rvol=2, traded_value=1000,
                              symbol="AAA")
        scores[2] = candidate(2, timestamp, 70, rvol=2, traded_value=1000,
                              symbol="BBB")
        scores[3] = candidate(3, timestamp, 70, rvol=2.5, traded_value=500,
                              symbol="HIGH-RVOL")
        scores[4] = candidate(4, timestamp, 70, rvol=2, traded_value=2000,
                              symbol="HIGH-VALUE")
        symbols = {score.instrument_id: score.instrument_id for score in scores}
        symbols["I00"] = "CHOP"
        symbols["I01"] = "AAA"
        symbols["I02"] = "BBB"
        symbols["I03"] = "HIGH-RVOL"
        symbols["I04"] = "HIGH-VALUE"
        result = snapshot(timestamp, tuple(scores), symbols)[0]
        self.assertEqual(20, len(result.bullish))
        self.assertNotIn("I00", {row.instrument_id for row in result.bullish})
        self.assertEqual("AAA", result.bullish[2].symbol)
        self.assertEqual(["HIGH-RVOL", "HIGH-VALUE", "AAA", "BBB"],
                         [row.symbol for row in result.bullish[:4]])
        self.assertEqual(list(range(1, 21)), [row.rank for row in result.bullish])
        bearish = candidate(30, timestamp, 75, direction="bearish", symbol="DOWN")
        both_sides = build_board_snapshots(tuple(scores) + (bearish,), symbols)[0]
        self.assertEqual("I30", both_sides.bearish[0].instrument_id)

    def test_hysteresis_exact_entry_and_exit_margins(self):
        t1, t2 = START + timedelta(minutes=5), START + timedelta(minutes=10)
        first = tuple(candidate(i, t1, 80 if i < 20 else 79,
                               symbol=f"S{i:02}") for i in range(21))
        symbols = {row.instrument_id: f"S{i:02}" for i, row in enumerate(first)}
        first_board = build_board_snapshots(first, symbols)[0]
        self.assertEqual("I00", first_board.bullish[0].instrument_id)
        self.assertEqual("I19", first_board.bullish[-1].instrument_id)

        # A new entrant exactly two points above the prior cutoff qualifies.
        next_scores = tuple(candidate(i, t2, 76 if i == 19 else
                                      (82 if i == 20 else 80), symbol=f"S{i:02}")
                            for i in range(21))
        two_points = build_board_snapshots(first + next_scores, symbols)[-1]
        self.assertIn("I20", {row.instrument_id for row in two_points.bullish})
        self.assertNotIn("I19", {row.instrument_id for row in two_points.bullish})

        # Incumbents exactly three below the previous score cutoff can remain;
        # a score below that boundary is removed.
        boundary_scores = tuple(candidate(i, t2, 77 if i == 19 else 80,
                                          symbol=f"S{i:02}") for i in range(20))
        boundary = build_board_snapshots(first[:20] + boundary_scores,
                                         symbols)[-1]
        self.assertIn("I19", {row.instrument_id for row in boundary.bullish})
        below_scores = tuple(candidate(i, t2, 76.99 if i == 19 else 80,
                                       symbol=f"S{i:02}") for i in range(20))
        below = build_board_snapshots(first[:20] + below_scores, symbols)[-1]
        self.assertNotIn("I19", {row.instrument_id for row in below.bullish})

    def test_session_reset_choppy_and_unavailable_rows_do_not_carry(self):
        t1, t2 = START + timedelta(minutes=5), START + timedelta(minutes=10)
        members = tuple(candidate(i, t1, 80, symbol=f"S{i:02}") for i in range(20))
        next_members = tuple(candidate(i, t2, 80, symbol=f"S{i:02}") for i in range(19))
        invalid = replace(candidate(19, t2, 100),
                          result=ScoreResult(False, None, {}, "missing_input"))
        symbols = {f"I{i:02}": f"S{i:02}" for i in range(20)}
        out = build_board_snapshots(members + next_members + (invalid,), symbols)
        self.assertEqual(19, len(out[-1].bullish))
        self.assertNotIn("I19", {row.instrument_id for row in out[-1].bullish})

    def test_replay_boards_and_scores_are_prefix_causal_and_deterministic(self):
        bars = [replace(bar, symbol="SCORE-X", adx14=25)
                for bar in scoring_session()]
        prefix = replay(bars[:15])
        complete = replay(bars)
        self.assertEqual(prefix.scores,
                         tuple(score for score in complete.scores
                               if score.timestamp <= bars[14].candle.timestamp))
        self.assertEqual(prefix.boards,
                         tuple(board for board in complete.boards
                               if board.timestamp <= bars[14].candle.timestamp))
        self.assertTrue(any(board.bullish or board.bearish for board in complete.boards))
        self.assertEqual(complete, replay(bars))


if __name__ == "__main__":
    unittest.main()
