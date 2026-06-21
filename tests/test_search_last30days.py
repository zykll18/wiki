import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.search_last30days import (
    append_pending,
    build_last30days_command,
    render_diagnostics_section,
    render_last30days_overview,
)


class SearchLast30DaysTests(unittest.TestCase):
    def test_append_pending_uses_supplied_root(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "raw" / "search" / "last30days" / "sample.md"
            output.parent.mkdir(parents=True)
            output.write_text("# sample\n", encoding="utf-8")

            append_pending(root, output)

            pending = (root / "raw" / "inbox" / "pending.md").read_text(encoding="utf-8")
            self.assertIn("raw/search/last30days/sample.md", pending)

    def make_args(self, **overrides: object) -> SimpleNamespace:
        defaults = {
            "topic": "loop engineering",
            "emit": "md",
            "days": 30,
            "sources": "x,github",
            "web_backend": "none",
            "quick": True,
            "depth": None,
            "debug": False,
            "save_suffix": "",
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_builds_deep_command(self) -> None:
        command = build_last30days_command(
            self.make_args(depth="deep"),
            Path("/skills/last30days/scripts/last30days.py"),
            Path("/tmp/last30days"),
        )

        self.assertIn("--deep", command)
        self.assertNotIn("--quick", command)

    def test_builds_default_depth_command(self) -> None:
        command = build_last30days_command(
            self.make_args(depth="default", quick=True),
            Path("/skills/last30days/scripts/last30days.py"),
            Path("/tmp/last30days"),
        )

        self.assertNotIn("--deep", command)
        self.assertNotIn("--quick", command)

    def test_renders_search_diagnostics(self) -> None:
        diagnostics = render_diagnostics_section(
            "Bird error: Search timed out after 30s\n"
            "No GitHub token available (set GITHUB_TOKEN or install gh CLI)\n"
            "Permission denied reading Cookies.binarycookies\n"
        )

        self.assertIn("## 抓取诊断", diagnostics)
        self.assertIn("X/Bird 搜索超时", diagnostics)
        self.assertIn("GitHub 未认证", diagnostics)
        self.assertIn("浏览器 Cookie 读取权限不足", diagnostics)

    def test_renders_bird_backend_failure(self) -> None:
        diagnostics = render_diagnostics_section("Bird error: Bird search failed\n")

        self.assertIn("X/Bird 后端搜索失败", diagnostics)

    def test_renders_ranked_cluster_table(self) -> None:
        text = """# last30days v3.3.2: loop engineer

- Date range: 2026-05-18 to 2026-06-17
- Sources: 2 active (Reddit, Youtube)

## Ranked Evidence Clusters

### 1. Loop Engineering in 9 Minutes (score 38, 1 item, sources: Youtube)
1. [youtube] Loop Engineering in 9 Minutes
   - 2026-06-13 | Developers Digest | [19,004views, 262likes, 25cmt] | score:38
   - URL: https://www.youtube.com/watch?v=nKlF15Ic78w

### 2. Got rejected from a GTM Engineer role (score 43, 1 item, sources: Reddit)
1. [reddit] Got rejected from a GTM Engineer role
   - 2026-06-14 | r/gtmengineering | [29cmt] | score:43
   - URL: https://www.reddit.com/r/gtmengineering/comments/example/

## Source Coverage

- Reddit: 2 items
- X: 0 items
- Youtube: 6 items
"""

        overview = render_last30days_overview(text)

        self.assertIn("## 结果概览", overview)
        self.assertIn("| 1 | [Loop Engineering in 9 Minutes](https://www.youtube.com/watch?v=nKlF15Ic78w) | Youtube | 38 | 2026-06-13 | Developers Digest |", overview)
        self.assertIn("## 来源覆盖", overview)
        self.assertIn("| X | 0 |", overview)
        self.assertIn("## 使用限制", overview)

    def test_does_not_duplicate_existing_overview(self) -> None:
        text = "# Title\n\n## 结果概览\n\nAlready enhanced.\n"

        overview = render_last30days_overview(text)

        self.assertEqual(overview, "")


if __name__ == "__main__":
    unittest.main()
