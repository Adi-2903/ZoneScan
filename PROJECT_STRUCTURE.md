# ZoneScan — Project & File Structure Reference

> **Note**: This is a temporary/quick reference document mapping the entire repository structure, document purposes, and service architecture. You can retain or delete this file anytime.

---

## 1. High-Level Repository Tree

```text
ZoneScan/
├── AGENTS.md                          # Mandatory instructions, rules, and guardrails for AI agents & contributors
├── README.md                          # Project overview, setup instructions, quickstart, and current status
├── PROJECT_STRUCTURE.md               # [This file] Complete structural map and doc reference
├── skills-lock.json                   # Agent skills lockfile
├── .gitattributes                     # Git attribute configuration
│
├── .github/
│   └── copilot-instructions.md        # GitHub Copilot development context & rules
│
├── .agents/                           # Local agent configuration, skills, and tools
│   └── skills/                        # Workspace-specific skills (e.g. design, brand, slides)
│
├── design-system/
│   └── zonescan/
│       └── MASTER.md                  # Authoritative Design System tokens, styles, typography, and theme definitions
│
├── docs/                              # Project documentation & engineering specifications
│   ├── 00_PROJECT_BRIEF.md            # Vision, scope, and the six workspaces definition
│   ├── 01_PRODUCT_REQUIREMENTS.md     # Feature requirements, user stories, and acceptance criteria
│   ├── 02_UX_FLOWS.md                 # User journeys, interaction specifications, and screen layouts
│   ├── 03_ARCHITECTURE.md             # System architecture, data flow, modular monolith design, SSE pipelines
│   ├── 04_MARKET_DATA.md              # Market data providers, ingestion rules, and licensing guardrails
│   ├── 05_ALGORITHMS.md               # Scoring logic, indicator calculations, order blocks, liquidity, and swing detection
│   ├── 06_API_CONTRACTS.md            # REST API & SSE endpoint schemas, payload formats, and status codes (/api/v1)
│   ├── 07_DATA_MODEL.md               # Database schemas, relational tables, and evidence tracking
│   ├── 08_SECURITY_PRIVACY_COMPLIANCE.md # Regulatory compliance (SEBI non-advisory), auth, and security practices
│   ├── 09_TESTING_BACKTESTING.md      # Testing strategy, fixture replay, backtesting methodology, validation
│   ├── 10_DEPLOYMENT_OPERATIONS.md    # Production deployment, Docker, CI/CD, monitoring, maintenance windows
│   ├── 11_ROADMAP.md                  # Milestone gates (Gate 0 through Gate 4), phase timeline, and release gates
│   ├── 12_DECISIONS.md                # Immutable Architecture Decision Records (ADRs)
│   ├── 13_OPEN_QUESTIONS.md           # Active open blockers, risks, and unresolved product questions
│   ├── 14_DESIGN_SYSTEM.md            # Design language summary, UI components, color palettes, and accessibility
│   ├── 15_GLOSSARY.md                 # Domain terminology (SMC, liquidity pools, order blocks, financial terms)
│   ├── 16_REFERENCES.md               # Reference papers, industry benchmarks, and source material
│   ├── 17_CHANGELOG.md                # Version history and notable milestone changes
│   ├── 18_DATA_PROVIDER_EVALUATION.md # Deep evaluation of market data vendors (Upstox, TrueData, etc.)
│   ├── 19_FINANCIAL_INTELLIGENCE.md   # Workspaces 2–6 specifications (Supply chain, segments, shareholding, filings)
│   ├── 20_COMPANY_INTELLIGENCE_IMPLEMENTATION.md # Frontend implementation details for company intelligence modules
│   ├── 20_REAL_DATA_PILOT_SPEC.md     # Upstox pilot integration, rate limits, and verification plan
│   └── DEFINITION_OF_DONE.md          # Acceptance checklist for tasks, PRs, and releases
│
├── apps/
│   └── web/                           # Next.js 14+ Frontend Application (TypeScript, Tailwind, Radix UI)
│       ├── package.json               # Frontend dependencies and npm scripts
│       ├── tsconfig.json              # TypeScript compiler configuration
│       ├── next.env.d.ts              # Next.js type declarations
│       ├── .env.example               # Frontend environment template
│       ├── .env.local                 # Local frontend environment variables
│       └── src/
│           ├── app/
│           │   ├── layout.tsx         # Root app layout, font configs, theme provider
│           │   ├── page.tsx           # Main workspace dashboard (Market Scanner, Heatmap, Intelligence)
│           │   └── globals.css        # Global CSS, theme variables, and Tailwind base styles
│           ├── components/
│           │   ├── ZoneChart.tsx      # Interactive candlestick & zone chart visualization
│           │   └── company/           # Financial Intelligence / Company Workspace components
│           │       ├── CompanyIntelligence.tsx    # Master container for company intelligence
│           │       ├── EvidenceBadge.tsx          # Provenance badge (Disclosed, Inferred, Unconfirmed, Unavailable)
│           │       ├── FilingList.tsx             # Regulatory filings list with source links
│           │       ├── FinancialTable.tsx         # Multi-period financial metrics and statements
│           │       ├── KPICard.tsx                # High-level financial KPIs with confidence markers
│           │       ├── MetricSparkline.tsx        # Mini trend sparklines for quick metric evaluation
│           │       ├── RelationshipMap.tsx        # Interactive node-graph for customers, suppliers, competitors
│           │       ├── SegmentChart.tsx           # Revenue and margin breakdown by business segment
│           │       ├── ShareholdingBar.tsx        # Ownership breakdown (Promoter, FII, DII, Public)
│           │       ├── SourcePanel.tsx            # Audit panel displaying filing sources and citation excerpts
│           │       └── SupplyChainSimulator.tsx   # Interactive cascade impact simulator
│           └── lib/
│               ├── api.ts                         # Client-side API fetchers and SSE event stream handlers
│               ├── calculations/
│               │   ├── supply-chain-impact.ts     # Client-side simulation logic for supply disruption
│               │   └── supply-chain-impact.test.ts# Unit tests for supply chain simulator
│               └── fixtures/
│                   └── company-intelligence.ts    # Synthetic fixtures for financial intelligence pilot
│
└── services/
    └── api/                           # Python 3.11+ Backend Analytics Engine & FastAPI Service
        ├── pyproject.toml             # Python dependencies, Ruff, pytest, and project metadata
        ├── examples/
        │   ├── fetch_upstox_sample.py # Sample script querying Upstox historical candles
        │   ├── replay_synthetic.py    # CLI tool to run minute-by-minute fixture replay
        │   └── score_synthetic.py     # CLI tool to generate and print synthetic board scores
        ├── src/
        │   └── zonescan/
        │       ├── __init__.py        # Package initialization
        │       ├── app.py             # FastAPI entrypoint, middleware, and /api/v1 routes
        │       ├── analytics_service.py # Core orchestration service connecting provider, cache, and scoring
        │       ├── boards.py          # Authoritative minute-board publishing, ranking, and snapshot generation
        │       ├── choppy.py          # Market regime detection (Choppy vs Trending filter)
        │       ├── early_move.py      # Early momentum shift and expansion detection algorithms
        │       ├── evaluation.py      # Post-bar outcome evaluation and accuracy tracking
        │       ├── fixtures.py        # Deterministic market data fixture generators (for tests and offline replay)
        │       ├── indicators.py      # Core technical indicators (EMA, ATR, RSI, VWAP)
        │       ├── liquidity.py       # Liquidity sweep and pool detection
        │       ├── models.py          # Pydantic schemas for candles, zones, scores, boards, and requests
        │       ├── order_blocks.py    # Institutional order block / supply-demand zone identification
        │       ├── providers.py       # MarketDataProvider interface and SyntheticProvider
        │       ├── provider_config.py # Provider selection and environment configuration
        │       ├── replay.py          # Historical bar replay engine ensuring identical live/backtest execution
        │       ├── scoring.py         # Multi-factor algorithmic scoring engine (0–100 scale)
        │       ├── structure.py       # Market structure analysis (Swing High/Low, BOS, CHoCH)
        │       ├── synthetic_analytics.py # Mock financial intelligence data generator for Workspaces 2–6
        │       └── upstox.py          # Upstox API client adapter implementing MarketDataProvider
        └── tests/
            ├── test_api.py            # FastAPI route tests and SSE streaming validation
            ├── test_boards.py         # Board generation and ranking tests
            ├── test_choppy.py         # Choppy filter unit tests
            ├── test_early_move.py     # Early move detection tests
            ├── test_evaluation.py     # Post-bar evaluation tests
            ├── test_foundation.py     # Base models and fixture integrity tests
            ├── test_indicators.py     # Technical indicator calculation tests
            ├── test_liquidity.py      # Liquidity sweep detection tests
            ├── test_order_blocks_replay.py # Order block replay and persistence tests
            ├── test_replay_scoring.py # Historical replay vs live parity tests
            ├── test_scoring.py        # Score ranking, weight calculation, and edge-case tests
            └── test_upstox.py         # Upstox integration and mock client tests
```

---

## 2. Documentation Directory Map (`docs/`)

| File | Title / Domain | Purpose & Key Topics |
| :--- | :--- | :--- |
| [`00_PROJECT_BRIEF.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/00_PROJECT_BRIEF.md) | Project Brief | High-level product thesis, non-advisory stance, and summary of the 6 core workspaces. |
| [`01_PRODUCT_REQUIREMENTS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/01_PRODUCT_REQUIREMENTS.md) | PRD & Features | P0/P1/P2/P3 functional and non-functional requirements, user stories, acceptance criteria. |
| [`02_UX_FLOWS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/02_UX_FLOWS.md) | UX & Flows | Workspace interaction flows, layout hierarchy, mobile responsiveness, empty/error states. |
| [`03_ARCHITECTURE.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/03_ARCHITECTURE.md) | Architecture | System design, single-scoring-worker invariant, SSE event flow, and caching model. |
| [`04_MARKET_DATA.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/04_MARKET_DATA.md) | Market Data | Data ingestion boundaries, candle integrity, exchange hours (`Asia/Kolkata`), provider interfaces. |
| [`05_ALGORITHMS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/05_ALGORITHMS.md) | Algorithms | Mathematical formulas for indicators, order block validation, liquidity sweeps, and composite score (0–100). |
| [`06_API_CONTRACTS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/06_API_CONTRACTS.md) | API Contracts | Versioned `/api/v1` specs: `/board/current`, `/board/events` (SSE), `/zones/{symbol}`, `/replay`. |
| [`07_DATA_MODEL.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/07_DATA_MODEL.md) | Data Model | Relational schema definitions, timestamps, and Financial Intelligence tables (`evidence_status`). |
| [`08_SECURITY_PRIVACY_COMPLIANCE.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/08_SECURITY_PRIVACY_COMPLIANCE.md) | Security & Legal | SEBI non-advisory compliance, credential management, cookie auth, CSRF, and threat modeling. |
| [`09_TESTING_BACKTESTING.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/09_TESTING_BACKTESTING.md) | Testing & Replay | Backtesting methodology, fixture determinism, parity checks between live scoring and historical replay. |
| [`10_DEPLOYMENT_OPERATIONS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/10_DEPLOYMENT_OPERATIONS.md) | DevOps & Ops | Containerization, deployment rules (never deploy during NSE market hours), health monitoring. |
| [`11_ROADMAP.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/11_ROADMAP.md) | Roadmap & Gates | Gate 0 (Spec), Gate 1 (Pilot), Gate 2 (Live Engine), Gate 3 (Financial Intel), Gate 4 (Public). |
| [`12_DECISIONS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/12_DECISIONS.md) | Decisions (ADRs) | Accepted architectural records (e.g., SSE over WebSockets, modular monolith, no live execution). |
| [`13_OPEN_QUESTIONS.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/13_OPEN_QUESTIONS.md) | Open Questions | Tracked risks, data licensing questions, provider evaluations, and unresolved items. |
| [`14_DESIGN_SYSTEM.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/14_DESIGN_SYSTEM.md) | Design Tokens | Colors (Bullish Green, Bearish Red, Alert Amber), accessible typography, and UI guidelines. |
| [`15_GLOSSARY.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/15_GLOSSARY.md) | Glossary | Explanations of SMC concepts, order blocks, liquidity sweeps, fair value gaps, and market terms. |
| [`16_REFERENCES.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/16_REFERENCES.md) | References | Academic papers, market microstructure books, and regulatory references. |
| [`17_CHANGELOG.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/17_CHANGELOG.md) | Changelog | Chronological record of major releases and architectural iterations. |
| [`18_DATA_PROVIDER_EVALUATION.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/18_DATA_PROVIDER_EVALUATION.md) | Provider Eval | Comparison matrix of Indian market data providers (Upstox, TrueData, Zerodha, GlobalDataFeeds). |
| [`19_FINANCIAL_INTELLIGENCE.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/19_FINANCIAL_INTELLIGENCE.md) | Financial Intel | Scope for Workspaces 2–6: Supply Chain, Segment Intelligence, Shareholding, and Regulatory Filings. |
| [`20_COMPANY_INTELLIGENCE_IMPLEMENTATION.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/20_COMPANY_INTELLIGENCE_IMPLEMENTATION.md) | Company Intel UI | Documentation of Next.js components, state management, and evidence badge integration. |
| [`20_REAL_DATA_PILOT_SPEC.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/20_REAL_DATA_PILOT_SPEC.md) | Real Data Pilot | Specification for the Upstox API pilot data feed and rate-limit guardrails. |
| [`DEFINITION_OF_DONE.md`](file:///d:/PROJECTS/A%20ZoneScan/ZoneScan/docs/DEFINITION_OF_DONE.md) | Definition of Done | Quality gates, test coverage expectations, and documentation checklists before merging. |

---

## 3. Core Applications & Services

### Frontend: `apps/web/`
- **Framework**: Next.js 14 (App Router) + TypeScript + Tailwind CSS.
- **Port**: `http://localhost:3000`
- **Key Modules**:
  - `page.tsx`: Core dashboard combining the ranked market scanner, interactive zone charts, and company intelligence tabs.
  - `components/company/`: Comprehensive suite of financial analysis tools (Supply Chain Simulator, Relationship Network Map, Segment Charts, Ownership breakdown, and Evidence-backed filings).
  - `lib/api.ts`: API client connecting to backend `/api/v1` with SSE subscription handling.

### Backend: `services/api/`
- **Framework**: Python 3.11+ / FastAPI / Pydantic.
- **Port**: `http://localhost:8000`
- **Key Invariants**:
  - Authoritative minute-board calculation (`boards.py` & `scoring.py`).
  - Provider neutrality: `MarketDataProvider` protocol (`providers.py`) implemented by `SyntheticProvider` and `UpstoxProvider`.
  - Deterministic replay parity (`replay.py`) ensuring backtests and live trading engines run the exact same logic without lookahead bias.
