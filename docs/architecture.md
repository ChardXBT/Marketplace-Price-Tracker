# Architecture

The public implementation separates collection, analysis, and decisions so
each layer can be tested without a browser or marketplace account.

```text
                 normalized identity and source records
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              v                                 v
      listing opportunity path          buy-order depth path
      ────────────────────────          ────────────────────
      deduplicate                       support share
      verify identity                   concentration
      compare reference                 breadth
      score confidence                  pump score
              │                                 │
              └────────────────┬────────────────┘
                               v
                   fail-closed decision planner
                               │
                               v
                 non-executable intent or hold
```

## Module boundaries

### `pipeline.py`

Defines immutable listing and opportunity records. It performs normalization,
deduplication, identity validation, comparison, confidence classification, and
one-intent-per-item protection.

### `market_shape.py`

Converts normalized order-book levels into support share, concentration,
breadth, and an illustrative pump-risk score. Empty or invalid depth produces
the most conservative result.

### `bidder.py`

Combines a verified opportunity with market shape. Elevated shape produces a
hold, lower confidence produces review, and a consistent result produces a
non-executable simulated bid intent.

### `cli.py`

Runs both public paths with deterministic synthetic fixtures and prints one
combined audit report.

## Safety boundaries

- No source adapter is connected to a real marketplace.
- Identity ambiguity blocks analysis.
- Missing depth blocks bid planning.
- Duplicate candidates cannot create repeated intents.
- Unknown outcomes are never retried as if they were definitive failures.
- Every public decision has `executable=false`.
- Real thresholds, identifiers, credentials, and request formats are absent.
