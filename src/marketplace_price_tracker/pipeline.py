from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Listing:
    item: str
    source: str
    ask: Decimal
    reference: Decimal
    liquidity: int
    identity_verified: bool = True


@dataclass(frozen=True)
class Opportunity:
    item: str
    source: str
    ask: Decimal
    reference: Decimal
    discount_percent: Decimal
    confidence: str


class PriceTracker:
    """Auto Buyer demo with fake inputs and no live connections."""

    def normalize(self, listings: list[Listing]) -> list[Listing]:
        unique: dict[tuple[str, str], Listing] = {}
        for listing in listings:
            key = (listing.item.casefold().strip(), listing.source.casefold().strip())
            current = unique.get(key)
            if current is None or listing.ask < current.ask:
                unique[key] = listing
        return sorted(unique.values(), key=lambda row: (row.item, row.source))

    def analyze(self, listings: list[Listing]) -> list[Opportunity]:
        opportunities: list[Opportunity] = []
        for listing in self.normalize(listings):
            if not listing.identity_verified or listing.ask <= 0 or listing.reference <= 0:
                continue
            discount = ((listing.reference - listing.ask) / listing.reference * 100).quantize(
                Decimal("0.1")
            )
            if discount <= 0:
                continue
            confidence = "high" if listing.liquidity >= 70 else "review"
            opportunities.append(
                Opportunity(
                    listing.item,
                    listing.source,
                    listing.ask,
                    listing.reference,
                    discount,
                    confidence,
                )
            )
        return sorted(
            opportunities,
            key=lambda row: (-row.discount_percent, row.item, row.source),
        )

    def plan_orders(self, opportunities: list[Opportunity]) -> list[dict[str, str]]:
        """Create non-executable intents after duplicate and confidence checks."""
        planned: list[dict[str, str]] = []
        seen: set[str] = set()
        for opportunity in opportunities:
            identity = opportunity.item.casefold().strip()
            if identity in seen or opportunity.confidence != "high":
                continue
            seen.add(identity)
            planned.append(
                {
                    "item": opportunity.item,
                    "source": opportunity.source,
                    "action": "SIMULATE_ORDER_INTENT",
                    "safety": "identity recheck required before any live adapter",
                }
            )
        return planned


def demo_tracker() -> tuple[PriceTracker, list[Listing]]:
    tracker = PriceTracker()
    listings = [
        Listing("Synthetic Rifle | Aurora", "CS Marketplace A", Decimal("42.00"), Decimal("50.00"), 86),
        Listing("Synthetic Rifle | Aurora", "CS Marketplace A", Decimal("44.00"), Decimal("50.00"), 86),
        Listing("Synthetic Pistol | Circuit", "CS Marketplace B", Decimal("18.50"), Decimal("20.00"), 74),
        Listing("Synthetic SMG | Transit", "CS Marketplace C", Decimal("11.20"), Decimal("12.00"), 41),
        Listing("Unverified Example", "CS Marketplace B", Decimal("5.00"), Decimal("9.00"), 99, False),
    ]
    return tracker, listings
