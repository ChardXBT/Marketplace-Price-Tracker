from __future__ import annotations

import argparse

from .pipeline import demo_tracker


def render_demo() -> str:
    tracker, listings = demo_tracker()
    normalized = tracker.normalize(listings)
    opportunities = tracker.analyze(listings)
    intents = tracker.plan_orders(opportunities)

    lines = [
        "MARKETPLACE PRICE TRACKER  |  synthetic read-only dry-run",
        "=" * 76,
        f"Inputs: {len(listings)}   Normalized: {len(normalized)}   Opportunities: {len(opportunities)}",
        "",
        "ITEM                          SOURCE              ASK      REFERENCE  SIGNAL   CONFIDENCE",
    ]
    for row in opportunities:
        lines.append(
            f"{row.item:<29} {row.source:<19} ${row.ask:>6}  ${row.reference:>8}  "
            f"{row.discount_percent:>5}%   {row.confidence}"
        )
    lines.extend(["", "SAFE ORDER PLANNER"])
    for intent in intents:
        lines.append(
            f"  READY  {intent['item']}  -> {intent['action']}  (non-executable)"
        )
    lines.extend(
        [
            "",
            "Safety gates: duplicate blocked | identity checked | uncertain listing skipped",
            "Result: synthetic analysis complete; no login, browser, API, or purchase used.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the safe marketplace tracking demonstration")
    parser.add_argument("--dry-run", action="store_true", help="retained for explicitness; all runs are synthetic")
    parser.parse_args()
    print(render_demo())


if __name__ == "__main__":
    main()
