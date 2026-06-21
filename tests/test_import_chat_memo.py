import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.import_chat_memo import build_parser, import_path


SAMPLE_CHAT = """Title: Hello World
URL: https://gemini.google.com/app/abc123
Platform: Gemini
Created: 2026-05-29 10:45:18
Messages: 2

User: [2026-05-29 10:45:18]
hello

AI: [2026-05-29 10:45:20]
world
"""


SAMPLE_CHAT_CN = """Title: 解释一下
URL: https://www.doubao.com/chat/38424937737753602
Platform: 豆包
Created: 2026-05-21 16:26:10
Messages: 3

User: [2026-05-21 16:26:10]
解释一下

AI: [2026-05-21 16:26:12]
好的
"""


def make_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


class ImportChatMemoTests(unittest.TestCase):
    def test_default_output_is_relative_to_current_working_directory(self) -> None:
        args = build_parser().parse_args(["exports.zip"])

        self.assertEqual(args.output, "raw/conversations")

    def test_imports_single_zip_into_markdown_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "raw" / "conversations"
            zip_path = root / "chat-memo.zip"
            make_zip(
                zip_path,
                {
                    "gemini_1.txt": SAMPLE_CHAT,
                    "doubao_2.txt": SAMPLE_CHAT_CN,
                },
            )

            report = import_path(zip_path, output_dir)

            self.assertEqual(report.imported, 2)
            self.assertEqual(report.skipped, 0)

            created_files = sorted(output_dir.glob("*.md"))
            self.assertEqual(len(created_files), 2)
            self.assertEqual(
                [file.name for file in created_files],
                [
                    "2026-05-21-doubao-chat-38424937.md",
                    "2026-05-29-gemini-hello-world-abc123.md",
                ],
            )
            self.assertEqual(created_files[1].read_text(encoding="utf-8"), SAMPLE_CHAT)

    def test_imports_all_zips_from_directory_and_skips_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "raw" / "conversations"
            export_dir = root / "exports"
            export_dir.mkdir()
            make_zip(export_dir / "first.zip", {"gemini_1.txt": SAMPLE_CHAT})
            make_zip(export_dir / "second.zip", {"gemini_dup.txt": SAMPLE_CHAT})

            report = import_path(export_dir, output_dir)

            self.assertEqual(report.imported, 1)
            self.assertEqual(report.skipped, 1)
            self.assertEqual(len(list(output_dir.glob("*.md"))), 1)

    def test_skips_invalid_zip_files_while_processing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "raw" / "conversations"
            export_dir = root / "exports"
            export_dir.mkdir()
            make_zip(export_dir / "valid.zip", {"gemini_1.txt": SAMPLE_CHAT})
            (export_dir / "broken.zip").write_text("not a real zip", encoding="utf-8")

            report = import_path(export_dir, output_dir)

            self.assertEqual(report.imported, 1)
            self.assertEqual(report.skipped, 1)
            self.assertIn("broken.zip", report.skipped_files)
            self.assertEqual(len(list(output_dir.glob("*.md"))), 1)

    def test_skips_plain_text_members_without_chat_memo_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "raw" / "conversations"
            zip_path = root / "mixed.zip"
            make_zip(
                zip_path,
                {
                    "gemini_1.txt": SAMPLE_CHAT,
                    "readme.txt": "plain text file without export headers\n",
                },
            )

            report = import_path(zip_path, output_dir)

            self.assertEqual(report.imported, 1)
            self.assertEqual(report.skipped, 1)
            self.assertIn("readme.txt", report.skipped_files)
            self.assertEqual(len(list(output_dir.glob("*.md"))), 1)

    def test_skips_duplicate_content_already_in_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "raw" / "conversations"
            output_dir.mkdir(parents=True)
            (output_dir / "custom-name.md").write_text(SAMPLE_CHAT, encoding="utf-8")

            zip_path = root / "chat-memo.zip"
            make_zip(zip_path, {"gemini_1.txt": SAMPLE_CHAT})

            report = import_path(zip_path, output_dir)

            self.assertEqual(report.imported, 0)
            self.assertEqual(report.skipped, 1)
            self.assertEqual(len(list(output_dir.glob("*.md"))), 1)

    def test_replaces_older_same_url_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "raw" / "conversations"
            output_dir.mkdir(parents=True)
            old_file = output_dir / "custom-career.md"
            old_file.write_text(
                SAMPLE_CHAT.replace("Messages: 2", "Messages: 2"),
                encoding="utf-8",
            )

            updated_chat = SAMPLE_CHAT.replace("Messages: 2", "Messages: 3") + "\nUser: later\n"
            zip_path = root / "chat-memo.zip"
            make_zip(zip_path, {"gemini_1.txt": updated_chat})

            report = import_path(zip_path, output_dir)

            self.assertEqual(report.imported, 1)
            self.assertEqual(report.skipped, 0)
            created_files = list(output_dir.glob("*.md"))
            self.assertEqual(len(created_files), 1)
            self.assertEqual(created_files[0].read_text(encoding="utf-8"), updated_chat)


if __name__ == "__main__":
    unittest.main()
