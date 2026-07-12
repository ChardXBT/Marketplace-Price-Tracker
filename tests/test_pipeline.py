from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_price_tracker import Listing, PriceTracker, demo_tracker  # noqa: E402


class PriceTrackerTests(unittest.TestCase):
    def test_normalization_keeps_best_duplicate(self) -> None:
        tracker, listings = demo_tracker()
        normalized = tracker.normalize(listings)
        rifles = [row for row in normalized if row.item == "Synthetic Rifle | Aurora"]
        self.assertEqual(len(rifles), 1)
        self.assertEqual(rifles[0].ask, Decimal("42.00"))

    def test_unverified_identity_never_becomes_opportunity(self) -> None:
        tracker, listings = demo_tracker()
        opportunities = tracker.analyze(listings)
        self.assertNotIn("Unverified Example", {row.item for row in opportunities})

    def test_duplicate_order_intents_are_blocked(self) -> None:
        tracker, listings = demo_tracker()
        opportunities = tracker.analyze(listings)
        intents = tracker.plan_orders(opportunities + opportunities)
        identities = [intent["item"] for intent in intents]
        self.assertEqual(len(identities), len(set(identities)))

    def test_review_confidence_is_not_auto_planned(self) -> None:
        tracker = PriceTracker()
        rows = [
            Listing("Synthetic Item", "CS Marketplace A", Decimal("8"), Decimal("10"), 20)
        ]
        opportunities = tracker.analyze(rows)
        self.assertEqual(opportunities[0].confidence, "review")
        self.assertEqual(tracker.plan_orders(opportunities), [])

    def test_non_positive_values_fail_closed(self) -> None:
        tracker = PriceTracker()
        rows = [Listing("Invalid", "CS Marketplace A", Decimal("0"), Decimal("10"), 100)]
        self.assertEqual(tracker.analyze(rows), [])


if __name__ == "__main__":
    unittest.main()
