# Marketplace Price Tracker

Marketplace Price Tracker is a public, synthetic reference implementation of
two related automation systems:

1. a cross-market scanner and auto-bid planner that compares current listings;
2. a bargain buy-order analyzer that evaluates order-book support before
   preparing a bid intent.

The production projects that inspired it operate across CS marketplaces. This
repository exposes the engineering architecture—normalization, identity
verification, market-shape analysis, duplicate prevention, and fail-closed
decisions—without including credentials, live adapters, private strategy
settings, or executable transaction code.

## System overview

```text
                           shared normalized item identity
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  │                                             │
                  v                                             v
      cross-market scanner / auto bidder             bargain buy-order analyzer
      ──────────────────────────────────             ──────────────────────────
      listing ingestion                              order-book depth
      exact identity validation                      demand/support calculation
      reference-price comparison                     concentration / pump check
      opportunity confidence                         pending-order reconciliation
      duplicate action guard                         safe bid-intent planning
                  │                                             │
                  └──────────────────────┬──────────────────────┘
                                         v
                         non-executable decisions + audit trail
```

Both paths use deterministic synthetic data. The public implementation ends at
an intent object and has no browser login, marketplace API key, account state,
or purchase endpoint.

## 1. Cross-market scanner and auto bidder

The scanner turns inconsistent listings from several abstract CS marketplace
sources into a single typed model. The auto-bid planner then determines whether
a signal is clear enough to become a non-executable intent.

### Pipeline

```text
source records
   -> schema validation
   -> identity normalization
   -> source/item deduplication
   -> reference comparison
   -> liquidity confidence
   -> ranked opportunity
   -> duplicate-safe simulated intent
```

### Important behaviors

| Stage | Engineering behavior |
| --- | --- |
| Ingestion | Accepts immutable records from interchangeable source adapters |
| Identity | Requires a verified normalized item before price analysis |
| Deduplication | Keeps one deterministic best observation per item/source key |
| Comparison | Computes a normalized signal against a synthetic reference value |
| Confidence | Separates strong signals from results that still need review |
| Planning | Produces at most one intent for a normalized item in one pass |
| Execution boundary | Stops before any live marketplace or browser adapter |

### Why identity comes first

A price difference is meaningless if two records refer to different variants.
The tracker therefore fails closed on uncertain identity instead of allowing a
large apparent discount to override missing evidence. This ordering also makes
the ranking explainable: each accepted row has a known item, source, observed
value, reference value, and confidence state.

## 2. Bargain buy-order analyzer

The buy-order side models the harder question: a low apparent price can be
unsafe when demand is shallow or concentrated in one artificial-looking
cluster. Before planning a bid, the system evaluates the shape of synthetic
order-book depth.

### Market-shape inputs

Each order-book level contains two normalized values:

- **relative distance** from the current reference region;
- **visible volume** at that level.

From these levels the analyzer derives:

- `support_share` — the fraction of visible depth close to the reference;
- `concentration` — the fraction controlled by the single largest level;
- `breadth` — how much of the expected depth range is populated;
- `pump_score` — a combined risk signal from concentrated, unsupported, or
  unusually narrow depth.

### Illustrative pump-check calculation

The public demo uses a normalized educational formula:

```text
pump_score =
    0.50 × concentration
  + 0.35 × (1 - support_share)
  + 0.15 × (1 - breadth)
```

This formula demonstrates the architecture, not private production tuning.
There are no real thresholds, target prices, item identifiers, or strategy
limits in this repository.

### Decision sequence

```text
verified opportunity
        │
        v
order-book available? ── no ──> HOLD
        │ yes
        v
pump risk elevated? ──── yes ─> HOLD
        │ no
        v
confidence high? ──────── no ──> REVIEW
        │ yes
        v
SIMULATE_BID_INTENT (never executable)
```

### Production concepts represented safely

The public planner mirrors the boundaries of a more complete system:

- reconcile existing and pending orders before proposing another action;
- preserve uncertain in-flight state rather than resubmitting;
- distinguish a seller counter-offer from a new independent opportunity;
- compare visible support with short-term price movement;
- avoid a bid when one depth level dominates the apparent demand;
- require a fresh identity and market-state check before any execution adapter.

No real order submission or marketplace-specific request logic is included.

## Shared reliability invariants

| Invariant | Result |
| --- | --- |
| Invalid values fail closed | Missing or non-positive observations are excluded |
| Unverified identity cannot advance | Price alone never overrides item ambiguity |
| One item produces one intent | Duplicate candidates cannot multiply actions |
| Uncertain outcomes are preserved | The planner does not assume success or failure |
| Concentrated depth blocks automation | Pump-like structure is surfaced as `HOLD` |
| Review remains distinct from approval | Lower-confidence signals stay human-visible |
| Public intents are never executable | The transaction boundary is absent by design |

## Data model

The reference implementation uses small immutable objects:

```text
Listing
  item, source, observed value, reference value, liquidity, identity proof

Opportunity
  item, source, comparison signal, confidence

OrderBookLevel
  relative distance, visible volume

MarketShape
  support share, concentration, breadth, pump score, elevated flag

BidDecision
  item, action, reason, executable=false
```

Keeping collection records separate from decisions makes the pipeline easier
to test, audit, and extend with additional adapters.

## Run the synthetic demonstration

```bash
git clone <repository-url>
cd Marketplace-Price-Tracker
python demo.py --dry-run
```

The report shows both sections: ranked cross-market signals and a separate
buy-order market-shape decision. Every value is synthetic.

## Tests

```bash
python -m unittest discover -s tests -v
```

The suite verifies:

- deterministic deduplication;
- unverified identity rejection;
- duplicate-intent blocking;
- fail-closed handling of invalid values and missing depth;
- review-only treatment of weaker signals;
- higher pump risk for concentrated versus distributed depth;
- bid holds when market shape is elevated;
- non-executable output for every decision path.

GitHub Actions runs the tests and dry-run report on every push and pull request.

## Repository layout

```text
.
├── docs/architecture.md
├── src/marketplace_price_tracker/
│   ├── pipeline.py       # Ingestion, normalization, comparison, ranking
│   ├── market_shape.py   # Support, concentration, breadth, pump analysis
│   ├── bidder.py         # Fail-closed non-executable bid decisions
│   └── cli.py            # Combined synthetic report
├── tests/
├── demo.py
└── pyproject.toml
```

## Public boundary

All item names, sources, prices, depth, and decisions are synthetic. The
repository contains no account details, browser profiles, marketplace-specific
identifiers, private strategy configuration, notification endpoints, or live
transaction capability.

See [the architecture notes](docs/architecture.md) for a compact component map.
