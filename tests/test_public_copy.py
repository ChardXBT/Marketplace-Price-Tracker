from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_price_tracker.cli import render_demo  # noqa: E402


class PublicCopyTests(unittest.TestCase):
    def test_readme_names_both_real_bot_roles_and_has_both_flows(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 1. Auto Buyer", readme)
        self.assertIn("## 2. Bargain Buy-Order Bot", readme)
        self.assertGreaterEqual(readme.count("```mermaid"), 3)
        self.assertNotIn("cross-market scanner", readme.lower())
        self.assertNotIn("auto-bid planner", readme.lower())
        self.assertNotIn("—", readme)
        self.assertNotIn("–", readme)

    def test_demo_uses_the_same_bot_names(self) -> None:
        output = render_demo()
        self.assertIn("AUTO BUYER", output)
        self.assertIn("BARGAIN BUY-ORDER BOT", output)
        self.assertNotIn("CROSS-MARKET", output)
        self.assertNotIn("AUTO-BID PLANNER", output)


if __name__ == "__main__":
    unittest.main()
