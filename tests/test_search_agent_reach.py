import tempfile
import unittest
from pathlib import Path

from scripts.search_agent_reach import (
    SearchRequest,
    append_pending,
    build_agent_reach_command,
    output_path_for,
    render_human_overview,
)


class SearchAgentReachTests(unittest.TestCase):
    def test_builds_bilibili_search_command(self) -> None:
        request = SearchRequest(platform="bilibili", action="search", target="AI 教程", limit=5)

        command = build_agent_reach_command(request)

        self.assertEqual(
            command,
            ["bili", "search", "AI 教程", "--type", "video", "--max", "5", "--json"],
        )

    def test_builds_xiaohongshu_search_command(self) -> None:
        request = SearchRequest(platform="xiaohongshu", action="search", target="Agent 笔记", limit=8)

        command = build_agent_reach_command(request)

        self.assertEqual(
            command,
            [
                "opencli",
                "xiaohongshu",
                "search",
                "Agent 笔记",
                "--limit",
                "8",
                "-f",
                "json",
                "--window",
                "background",
                "--site-session",
                "persistent",
            ],
        )

    def test_output_path_uses_platform_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = SearchRequest(platform="bilibili", action="search", target="AI 教程", limit=5)

            path = output_path_for(root, request)

            self.assertEqual(path.parent, root / "raw" / "search" / "agent-reach" / "bilibili")
            self.assertTrue(path.name.endswith("-bilibili-search.md"))

    def test_renders_bilibili_search_overview_table(self) -> None:
        request = SearchRequest(platform="bilibili", action="search", target="redis", limit=2)
        stdout = """
{"ok": true, "data": [{"bvid": "BV123", "title": "Redis 入门", "author": "作者A", "play": 1000, "duration": "57:51"}]}
"""

        overview = render_human_overview(request, stdout)

        self.assertIn("## 结果概览", overview)
        self.assertIn("| 1 | [Redis 入门](https://www.bilibili.com/video/BV123) | 作者A | 1000 | 57:51 | `BV123` |", overview)

    def test_renders_xiaohongshu_search_overview_table(self) -> None:
        request = SearchRequest(platform="xiaohongshu", action="search", target="AI Agent", limit=2)
        stdout = """
[{"rank": 1, "title": "Agent开发路线分享", "author": "学不秃头", "likes": "795", "published_at": "2026-06-10", "url": "https://www.xiaohongshu.com/search_result/abc"}]
"""

        overview = render_human_overview(request, stdout)

        self.assertIn("## 结果概览", overview)
        self.assertIn("| 1 | [Agent开发路线分享](https://www.xiaohongshu.com/search_result/abc) | 学不秃头 | 795 | 2026-06-10 |", overview)

    def test_append_pending_adds_relative_path_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "raw" / "search" / "agent-reach" / "bilibili" / "sample.md"
            output.parent.mkdir(parents=True)
            output.write_text("sample", encoding="utf-8")

            append_pending(root, output)
            append_pending(root, output)

            pending = (root / "raw" / "inbox" / "pending.md").read_text(encoding="utf-8")
            self.assertEqual(pending.count("raw/search/agent-reach/bilibili/sample.md"), 1)


if __name__ == "__main__":
    unittest.main()
