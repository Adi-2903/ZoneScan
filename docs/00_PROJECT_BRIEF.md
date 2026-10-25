# 00 — Project Brief

**Project:** ZoneScan (working codename)  
**Document status:** Baseline proposal; implementation has not started.  
**Last reviewed:** 2026-10-26  
**Market:** India; NSE F&O equity stocks. Nifty and Bank Nifty are contextual indicators, not part of the equity-stock ranking by default.

## Product summary

ZoneScan is a mobile-first web analytics terminal that scans the eligible NSE F&O equity universe during the trading session and presents ranked bullish and bearish stock lists, rule-based order-block zones, relevant price/liquidity levels, and market/sector context. The goal is to reduce repetitive manual chart scanning and help a trader decide which charts to inspect—not to tell a trader what action to take.

The app is a **scanner and analysis aid**, not a broker, exchange, investment adviser, research analyst, or automated trading system. That product description is not a legal classification; a qualified securities lawyer must review the actual features, outputs, and marketing before public launch.

## User problem

A trader may spend the first part of the session opening many charts, looking for directional movement, marking price zones, and trying to distinguish broad market movement from isolated stock movement. ZoneScan proposes a ranked board, explainable score, and pre-drawn context to make that review faster.

## Primary users

- Intraday traders examining NSE F&O equity stocks.
- Part-time traders with limited time during the opening hour.
- Learners who want consistent, explicitly explained chart annotations.

These are target personas, not validated customer research. Validate with user interviews before locking positioning or price.

## Core product loop

1. Open the board before or after the market opens.
2. See market status and whether the initial data is still settling.
3. Review the top bullish and bearish stocks, with rank, score, timestamp, and sector context.
4. Open a stock chart to inspect a potential zone and its supporting levels.
5. Optionally add it to a watchlist and create an alert.
6. The user independently decides what to do in their broker app; ZoneScan does not place an order.
7. Optionally log their own trade and review personal journal statistics.

## Product principles

1. **Explain, do not command.** Show calculations and chart levels without buy/sell calls or guaranteed outcomes.
2. **One screen, one fast decision.** The board should help users identify charts to inspect in under 10 seconds.
3. **Truthful about data.** Show source timestamps and delayed/stale/closed/synthetic states.
4. **No repainting.** Confirm analysis from closed candles and confirmed swings.
5. **Measure before marketing.** Backtest transparently; never invent hit rate, accuracy, or profit claims.
6. **Mobile first.** Core board works from 360 px width; Market X-Ray can use landscape or desktop layout.
7. **Legal access comes before monetization.** Data rights and regulatory review are launch gates.

## Scope assumptions

- Primary universe: current NSE F&O equity-stock list, refreshed from a permitted source; do not hardcode a permanent list of ~200 symbols.
- Nifty 50, Bank Nifty, and applicable sector indices provide context/bias, not stock rows in the core bullish/bearish equity boards.
- English UI for the first release; more languages are a later decision.
- INR pricing if monetized; no price is approved in this baseline.
- Responsive web app first; PWA is a later enhancement.
- The first analytics engine is deterministic and parameterized, not machine learning.

## Out of scope for the first release

- Broker order placement or account-level trading permissions.
- Automated or algorithmic execution.
- Personalized recommendations, explicit trade calls, price targets, or suggested stop-losses.
- A public social feed that lets staff or users post calls/targets.
- Native iOS/Android apps.
- AI-generated trading recommendations.
- Claims that an order block proves institutional orders or predicts price with certainty.

## Success measures to validate

- Board's minute cycle completes within the documented performance target.
- User can understand a row and open its chart within a few interactions on mobile.
- Percentage of symbols excluded for missing/stale data is visible to operators.
- Backtest metrics are reproducible and evaluated out-of-sample.
- Early beta users understand the scores and limitations without interpreting them as guaranteed recommendations.
- Data and legal gates are documented and approved before production monetization.

## Source basis and limits

The initial feature category was studied from public pages of OrderBlock and the detailed requirements supplied with this brief. The implementation, formulas, copy, brand, and UI must be independently created. See `16_REFERENCES.md` for current public sources and the limitations of this research.
