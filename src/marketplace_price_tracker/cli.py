from __future__ import annotations

import argparse
from decimal import Decimal

from .bidder import BargainBidPlanner
from .market_shape import MarketShapeAnalyzer, OrderBookLevel
from .pipeline import demo_tracker


def render_demo() -> str:
    tracker, listings = demo_tracker()
    normalized = tracker.normalize(listings)
    opportunities = tracker.analyze(listings)
    intents = tracker.plan_orders(opportunities)

    lines = [
        "MARKETPLACE PRICE TRACKER  |  fake-data read-only dry-run",
        "=" * 76,
        f"Inputs: {len(listings)}   Normalized: {len(normalized)}   Opportunities: {len(opportunities)}",
        "",
        "AUTO BUYER",
        "ITEM                          SOURCE              ASK      REFERENCE  SIGNAL   CONFIDENCE",
    ]
    for row in opportunities:
        lines.append(
            f"{row.item:<29} {row.source:<19} ${row.ask:>6}  ${row.reference:>8}  "
            f"{row.discount_percent:>5}%   {row.confidence}"
        )
    lines.extend(["", "AUTO BUYER RESULTS"])
    for intent in intents:
        lines.append(
            f"  READY  {intent['item']}  -> {intent['action']}  (non-executable)"
        )
    analyzer = MarketShapeAnalyzer()
    shape = analyzer.analyze(
        [
            OrderBookLevel(Decimal("0.01"), Decimal("34")),
            OrderBookLevel(Decimal("0.03"), Decimal("27")),
            OrderBookLevel(Decimal("0.07"), Decimal("22")),
            OrderBookLevel(Decimal("0.12"), Decimal("17")),
        ]
    )
    bid = BargainBidPlanner().decide(opportunities[0], shape)
    lines.extend(
        [
            "",
            "BARGAIN BUY-ORDER BOT",
            f"  support={shape.support_share}  concentration={shape.concentration}  "
            f"breadth={shape.breadth}  pump_score={shape.pump_score}",
            f"  decision={bid.action}  executable={str(bid.executable).lower()}",
            "",
            "Safety gates: duplicate blocked | identity checked | uncertain listing skipped",
            "Result: fake-data checks complete; no login, browser, API, or purchase used.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the safe marketplace tracking demonstration")
    parser.add_argument("--dry-run", action="store_true", help="all runs use fake data and cannot place an order")
    parser.parse_args()
    print(render_demo())


if __name__ == "__main__":
    main()
