from __future__ import annotations

from dataclasses import dataclass

from .market_shape import MarketShape
from .pipeline import Opportunity


@dataclass(frozen=True)
class BidDecision:
    item: str
    action: str
    reason: str
    executable: bool = False


class BargainBidPlanner:
    """Converts verified signals into non-executable public-demo decisions."""

    def decide(self, opportunity: Opportunity, shape: MarketShape) -> BidDecision:
        if shape.elevated:
            return BidDecision(
                opportunity.item,
                "HOLD",
                "market depth is too concentrated for automatic planning",
            )
        if opportunity.confidence != "high":
            return BidDecision(
                opportunity.item,
                "REVIEW",
                "price signal passed but confidence remains uncertain",
            )
        return BidDecision(
            opportunity.item,
            "SIMULATE_BID_INTENT",
            "identity, price signal, liquidity, and market shape are consistent",
        )
