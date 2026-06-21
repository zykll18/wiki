import tempfile
import unittest
from pathlib import Path

from scripts.vault_maintenance import (
    find_pending_raw_files,
    find_merge_candidates,
    find_orphan_pages,
    find_rewrite_candidates,
    find_weakly_linked_pages,
    lint_missing_required_sections,
    lint_query_writeback_workflow,
    lint_unlinked_verification_claims,
    lint_broken_wikilinks,
    lint_summary_raw_targets,
    lint_unexpected_root_notes,
    read_raw_context,
    suggest_syntheses_for_raw,
    iter_markdown_files,
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class VaultMaintenanceTests(unittest.TestCase):
    def test_accepts_public_root_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("README.md", "AGENTS.md", "index.md", "log.md"):
                write(root / name, f"# {name}\n")

            self.assertEqual(lint_unexpected_root_notes(root), [])

    def test_accepts_public_english_synthesis_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "wiki" / "syntheses" / "Source-Aware Environment Setup.md",
                "# Source-Aware Environment Setup\n"
                "## Current Judgment\nUse source boundaries.\n"
                "## Exceptions and Verification\n- See [[Conflict and Verification Register]]\n"
                "## Related Pages\n- [[Reproducible Python Environments]]\n- [[Python venv]]\n",
            )

            self.assertEqual(lint_missing_required_sections(root), [])

    def test_accepts_public_english_query_writeback_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "wiki" / "syntheses" / "Query and Writeback Workflow.md",
                "# Query and Writeback Workflow\n"
                "## Current Judgment\nRead maintained knowledge.\n"
                "## Writeback Decision\nChoose a destination.\n"
                "## Writeback Template\nRecord evidence and destination.\n"
                "## Exceptions and Verification\n- See [[Conflict and Verification Register]]\n"
                "## Related Pages\n- [[Source-Aware Environment Setup]]\n"
                "- [[Reproducible Python Environments]]\n",
            )

            self.assertEqual(lint_query_writeback_workflow(root), [])

    def test_finds_raw_files_without_summary_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "raw" / "conversations"
            summary_dir = root / "wiki" / "summaries"

            raw_a = raw_dir / "a.md"
            raw_b = raw_dir / "b.md"
            write(raw_a, "A")
            write(raw_b, "B")
            write(
                summary_dir / "sum.md",
                f"# 摘要\n\n- 原始文件：[a.md]({raw_a.resolve()})\n",
            )

            pending = find_pending_raw_files(root)

            self.assertEqual(pending, [raw_b.resolve()])

    def test_lints_broken_wikilinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = root / "wiki" / "topics" / "topic.md"
            other = root / "wiki" / "topics" / "other.md"
            write(note, "# Topic\n\nSee [[Other]] and [[Missing Page]].\n")
            write(other, "# Other\n")

            issues = lint_broken_wikilinks(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("Missing Page", issues[0])

    def test_ignores_raw_wikilinks_when_linting_broken_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "raw" / "search" / "github.md", "# Raw\n\n[[Bug]] upstream title.\n")
            write(root / "wiki" / "topics" / "topic.md", "# Topic\n\n[[Missing Page]]\n")

            issues = lint_broken_wikilinks(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("Missing Page", issues[0])
            self.assertNotIn("Bug", issues[0])

    def test_lints_missing_raw_target_in_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = root / "wiki" / "summaries" / "sum.md"
            missing_raw = root / "raw" / "conversations" / "missing.md"
            write(
                summary,
                f"# 摘要\n\n- 原始文件：[missing.md]({missing_raw})\n",
            )

            issues = lint_summary_raw_targets(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("missing.md", issues[0])

    def test_ignores_engineering_markdown_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "wiki" / "topics" / "Topic.md", "# Topic\n")
            write(root / "capture-pet" / "README.md", "[[Missing Engineering Link]]\n")
            write(root / "capture-pet" / "node_modules" / "debug" / "README.md", "[[Missing Package Link]]\n")

            markdown_files = iter_markdown_files(root)
            issues = lint_broken_wikilinks(root)

            self.assertEqual(markdown_files, [root / "wiki" / "topics" / "Topic.md"])
            self.assertEqual(issues, [])

    def test_ignores_raw_inbox_queue_when_finding_pending_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "raw" / "inbox" / "pending.md", "- [ ] raw/conversations/a.md\n")

            pending = find_pending_raw_files(root)

            self.assertEqual(pending, [])

    def test_lints_unexpected_root_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "index.md", "# Index\n")
            write(root / "log.md", "# Log\n")
            write(root / "AGENTS.md", "# Rules\n")
            write(root / "Loose Note.md", "# stray\n")

            issues = lint_unexpected_root_notes(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("Loose Note.md", issues[0])

    def test_suggests_relevant_synthesis_for_pending_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_file = root / "raw" / "web" / "pdf-note.md"
            write(
                raw_file,
                "\n".join(
                    [
                        "Title: PDF怎么读取",
                        "URL: https://example.com/pdf",
                        "Platform: Web",
                        "Created: 2026-05-31 10:00:00",
                        "Messages: 1",
                        "",
                        "User: [2026-05-31 10:00:00]",
                        "我想知道 PDF 读取、OCR 和布局解析应该怎么选",
                    ]
                ),
            )
            write(
                root / "wiki" / "syntheses" / "面向 AI 工作流的 PDF 读取路线.md",
                "# 面向 AI 工作流的 PDF 读取路线\n\n适合处理 PDF、OCR、布局解析和多模态读取。\n",
            )
            write(
                root / "wiki" / "syntheses" / "AI Agent、机器人与长期资源配置.md",
                "# AI Agent、机器人与长期资源配置\n\n讨论机器人和 AI Agent。\n",
            )

            suggestions = suggest_syntheses_for_raw(root, raw_file)

            self.assertGreaterEqual(len(suggestions), 1)
            self.assertEqual(suggestions[0].path.name, "面向 AI 工作流的 PDF 读取路线.md")
            self.assertGreater(suggestions[0].score, 0)

    def test_reads_context_from_non_chat_raw_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_file = root / "raw" / "search" / "last30days" / "agent-skill.md"
            write(
                raw_file,
                "# Last30Days\n\nAgent Skill negative transfer and meta-skill guidance.\n",
            )

            context = read_raw_context(raw_file)

            self.assertIn("Agent Skill negative transfer", context)

    def test_finds_orphan_pages_without_inbound_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            linked = root / "wiki" / "topics" / "Linked Topic.md"
            orphan = root / "wiki" / "topics" / "Orphan Topic.md"
            write(linked, "# Linked Topic\n")
            write(orphan, "# Orphan Topic\n")
            write(root / "index.md", "# Index\n\n- [[Linked Topic]]\n")

            orphans = find_orphan_pages(root)

            self.assertEqual(orphans, [orphan.resolve()])

    def test_finds_weakly_linked_topic_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            weak = root / "wiki" / "topics" / "Weak Topic.md"
            strong = root / "wiki" / "topics" / "Strong Topic.md"
            write(weak, "# Weak Topic\n\n## 相关来源\n- [[Only One]]\n")
            write(strong, "# Strong Topic\n\n[[One]] [[Two]]\n")

            weak_pages = find_weakly_linked_pages(root, min_links=2)

            self.assertEqual(weak_pages, [weak.resolve()])

    def test_finds_rewrite_candidates_from_multiple_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            topic = root / "wiki" / "topics" / "Windows Cleanup.md"
            write(topic, "# Windows Cleanup\n")
            for index in range(3):
                write(
                    root / "wiki" / "summaries" / f"summary-{index}.md",
                    "# Summary\n\n- 主主题：[[Windows Cleanup]]\n",
                )

            candidates = find_rewrite_candidates(root, summary_threshold=3)

            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0].path, topic.resolve())
            self.assertIn("3 summaries", candidates[0].reason)

    def test_finds_merge_candidates_with_similar_topic_titles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "wiki" / "topics" / "PDF Reading.md"
            second = root / "wiki" / "topics" / "PDF Reading Notes.md"
            unrelated = root / "wiki" / "topics" / "Hair Care.md"
            write(first, "# PDF Reading\n")
            write(second, "# PDF Reading Notes\n")
            write(unrelated, "# Hair Care\n")

            candidates = find_merge_candidates(root, min_score=0.5)

            self.assertEqual(len(candidates), 1)
            self.assertEqual({candidates[0].first, candidates[0].second}, {first.resolve(), second.resolve()})

    def test_lints_synthesis_missing_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "wiki" / "syntheses" / "Thin Synthesis.md",
                "# Thin Synthesis\n\n## 当前判断\n只有一个区块。\n",
            )

            issues = lint_missing_required_sections(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("例外与待验证", issues[0])

    def test_lints_unlinked_verification_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "wiki" / "topics" / "Risky Topic.md",
                "# Risky Topic\n\n## 例外与待验证\n- 待验证：这里缺少来源链接。\n",
            )

            issues = lint_unlinked_verification_claims(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("Risky Topic.md", issues[0])

    def test_lints_missing_query_writeback_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            issues = lint_query_writeback_workflow(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("missing query writeback workflow", issues[0])

    def test_accepts_complete_query_writeback_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "wiki" / "syntheses" / "查询与回写工作流.md",
                "\n".join(
                    [
                        "# 查询与回写工作流",
                        "",
                        "## 当前判断",
                        "先读 wiki，再回答。",
                        "",
                        "## 回写判定",
                        "回答后判断是否写回。",
                        "",
                        "## 回写模板",
                        "记录问题、结论和落点。",
                        "",
                        "## 例外与待验证",
                        "- 待验证内容参考 [[冲突与待验证清单]]",
                        "",
                        "## 相关页面",
                        "- [[AGENTS]]",
                        "- [[知识库入库判断样例]]",
                    ]
                ),
            )

            issues = lint_query_writeback_workflow(root)

            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
