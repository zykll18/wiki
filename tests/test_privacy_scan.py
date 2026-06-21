import tempfile
import unittest
from pathlib import Path

from scripts.privacy_scan import scan_repository


class PrivacyScanTests(unittest.TestCase):
    def test_detects_constructed_secrets_and_absolute_home_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            secrets = [
                "s" + "k-" + "abcdefgh12345678",
                "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456",
                "as" + "_sk_" + "abcdefghijklmnop",
                "Bear" + "er " + "abcdefghijklmnop",
            ]
            home_path = "/" + "Users/example/private-vault"
            lines = [f"token={secret}" for secret in secrets]
            lines.append(f"path={home_path}")
            (root / "leak.md").write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )

            findings = scan_repository(root)

            self.assertEqual(
                [finding.kind for finding in findings],
                ["secret", "secret", "secret", "secret", "absolute-user-path"],
            )
            self.assertTrue(all("[REDACTED]" in finding.excerpt for finding in findings))

    def test_detects_constructed_email_and_actual_private_journal_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            email = "real.person" + "@example.com"
            (root / "note.md").write_text(
                f"Contact {email}\n",
                encoding="utf-8",
            )
            private_journal = root / "raw" / "projects" / "demo"
            private_journal.mkdir(parents=True)
            (private_journal / "session.md").write_text("# private\n", encoding="utf-8")
            documentation = root / "docs" / "superpowers"
            documentation.mkdir(parents=True)
            (documentation / "reference.md").write_text(
                "Mention raw/" + "projects and " + email + "\n",
                encoding="utf-8",
            )

            findings = scan_repository(root)

            self.assertEqual(
                {finding.kind for finding in findings},
                {"email", "private-journal-path"},
            )
            self.assertEqual(
                sum(finding.kind == "email" for finding in findings),
                1,
            )

    def test_ignores_metadata_generated_directories_and_env_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            email = "ignored.person" + "@example.com"
            for directory in (".git", "node_modules", "dist", "__pycache__"):
                ignored = root / directory
                ignored.mkdir()
                (ignored / "leak.md").write_text(
                    f"Contact {email}\n",
                    encoding="utf-8",
                )
            (root / ".env.example").write_text(
                "TOKEN=" + "s" + "k-" + "abcdefgh12345678\n",
                encoding="utf-8",
            )

            findings = scan_repository(root)

            self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
