# 15 — Glossary

| Term | Meaning in this project |
|---|---|
| ATR | Average True Range; here usually ATR(14) on completed 5-minute candles, measured in price units. |
| BOS | Break of structure: completed candle closes beyond the latest confirmed swing high/low. |
| Choppy | A classification assigned when at least two configured low-trend/low-movement conditions hold. It is a rule, not a judgement about future price. |
| F&O | Futures and Options. The initial universe is eligible NSE F&O equity stocks. |
| FVG | Fair Value Gap, a three-candle price-imbalance pattern as defined in the algorithm spec. |
| Fresh zone | An order-block zone price has not revisited since formation. |
| Liquidity level | A rule-derived price reference such as equal highs/lows or session extremes; not a direct order-book measurement. |
| Mitigated zone | A zone invalidated by a completed close through its far side under the project rules. |
| OI | Open Interest in the selected futures contract. It must be tagged with contract identity and rollover handling. |
| Order block | Rule-defined zone using the last opposing candle before a qualifying displacement/BOS. It does not prove institutional orders existed there. |
| P0/P1/P2 | P0 = core MVP; P1 = first expansion; P2 = later. Release gates can block any priority. |
| PDH / PDL | Previous Day High / Previous Day Low. |
| PWH / PWL | Previous Week High / Previous Week Low. |
| Relative Volume (RVOL) | Volume compared with a documented baseline, preferably the same elapsed time over prior sessions. |
| Sector aligned | Sector's aggregate bias agrees with the stock's classified direction. Exact threshold is a versioned parameter. |
| Strength Score | Weighted 0–100 score used for ranking. It is a heuristic requiring backtest validation. |
| Early-Move Score | Provisional score combining recent OI, momentum and volume burst with a run penalty. It is not the same as chart liquidity. |
| Tested zone | Price revisited a zone, but a completed candle did not close through its invalidation side. |
| VWAP | Volume Weighted Average Price for the session. |
| Zone distance | Distance from current price to a relevant edge of an order-block zone; display sign/inside/outside convention explicitly. |
