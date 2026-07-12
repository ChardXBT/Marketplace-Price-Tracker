from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderBookLevel:
    """Synthetic order-book depth expressed without marketplace identifiers."""

    relative_distance: Decimal
    volume: Decimal


@dataclass(frozen=True)
class MarketShape:
    support_share: Decimal
    concentration: Decimal
    breadth: Decimal
    pump_score: Decimal
    elevated: bool


class MarketShapeAnalyzer:
    """Illustrative pump-risk model for the public demonstration.

    The formula is intentionally generic and uses normalized market shape. It
    is not production strategy configuration.
    """

    def __init__(
        self,
        *,
        support_band: Decimal = Decimal("0.08"),
        target_depth: int = 5,
        elevated_score: Decimal = Decimal("0.55"),
    ) -> None:
        self.support_band = support_band
        self.target_depth = target_depth
        self.elevated_score = elevated_score

    def analyze(self, levels: list[OrderBookLevel]) -> MarketShape:
        positive = [level for level in levels if level.volume > 0]
        total = sum((level.volume for level in positive), Decimal("0"))
        if not positive or total <= 0:
            return MarketShape(
                support_share=Decimal("0"),
                concentration=Decimal("1"),
                breadth=Decimal("0"),
                pump_score=Decimal("1"),
                elevated=True,
            )

        support = sum(
            (
                level.volume
                for level in positive
                if abs(level.relative_distance) <= self.support_band
            ),
            Decimal("0"),
        )
        support_share = support / total
        concentration = max(level.volume for level in positive) / total
        breadth = min(
            Decimal("1"),
            Decimal(len(positive)) / Decimal(max(1, self.target_depth)),
        )
        pump_score = (
            Decimal("0.50") * concentration
            + Decimal("0.35") * (Decimal("1") - support_share)
            + Decimal("0.15") * (Decimal("1") - breadth)
        ).quantize(Decimal("0.001"))
        return MarketShape(
            support_share=support_share.quantize(Decimal("0.001")),
            concentration=concentration.quantize(Decimal("0.001")),
            breadth=breadth.quantize(Decimal("0.001")),
            pump_score=pump_score,
            elevated=pump_score >= self.elevated_score,
        )
