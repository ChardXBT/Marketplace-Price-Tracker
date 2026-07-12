from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_price_tracker import (  # noqa: E402
    BargainBidPlanner,
    MarketShapeAnalyzer,
    Opportunity,
    OrderBookLevel,
)


class MarketShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = MarketShapeAnalyzer()

    def test_concentrated_depth_scores_higher_than_distributed_depth(self) -> None:
        concentrated = self.analyzer.analyze(
            [
                OrderBookLevel(Decimal("0.01"), Decimal("95")),
                OrderBookLevel(Decimal("0.20"), Decimal("5")),
            ]
        )
        distributed = self.analyzer.analyze(
            [
                OrderBookLevel(Decimal("0.01"), Decimal("25")),
                OrderBookLevel(Decimal("0.03"), Decimal("25")),
                OrderBookLevel(Decimal("0.05"), Decimal("25")),
                OrderBookLevel(Decimal("0.07"), Decimal("25")),
            ]
        )
        self.assertGreater(concentrated.pump_score, distributed.pump_score)
        self.assertTrue(concentrated.elevated)
        self.assertFalse(distributed.elevated)

    def test_missing_depth_fails_closed(self) -> None:
        shape = self.analyzer.analyze([])
        self.assertTrue(shape.elevated)
        self.assertEqual(shape.pump_score, Decimal("1"))

    def test_elevated_shape_blocks_bid_intent(self) -> None:
        opportunity = Opportunity(
            "Synthetic Item",
            "CS Marketplace A",
            Decimal("8"),
            Decimal("10"),
            Decimal("20"),
            "high",
        )
        shape = self.analyzer.analyze(
            [OrderBookLevel(Decimal("0.20"), Decimal("100"))]
        )
        decision = BargainBidPlanner().decide(opportunity, shape)
        self.assertEqual(decision.action, "HOLD")
        self.assertFalse(decision.executable)


if __name__ == "__main__":
    unittest.main()
