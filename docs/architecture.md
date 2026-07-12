# Architecture

This repository presents a public-safe slice of a larger marketplace
automation project. It uses synthetic inputs and stops at non-executable order
intents.

```text
source adapters -> normalization -> identity checks -> opportunity ranking
                                                       |
                                          duplicate and confidence gates
                                                       |
                                           simulated order intents only
```

## Engineering decisions

- **Normalized records** provide one internal model across multiple CS
  marketplaces.
- **Identity verification** fails closed before comparison or order planning.
- **Deterministic ranking** makes decisions reproducible and testable.
- **Duplicate prevention** ensures one item cannot produce repeated intents in
  the same planning pass.
- **Uncertainty is explicit.** Lower-confidence results remain visible for
  review but are never promoted automatically.
- **Execution is absent by design.** The public code has no credentials,
  browser profiles, marketplace adapters, or live-order endpoint.

The private production projects include independent monitoring and bargain
buy-order workflows. This repository combines their public architectural ideas
without exposing their integrations or strategy configuration.
