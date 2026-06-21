import tempfile
import unittest
from pathlib import Path

from scripts.validate_demo import validate_demo


class DemoValidationTests(unittest.TestCase):
    def test_reports_missing_required_layers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = validate_demo(Path(tmp))

            self.assertIn("missing raw sources", issues)
            self.assertIn("missing summaries", issues)
            self.assertIn("missing synthesis", issues)

    def test_accepts_repository_demo(self) -> None:
        root = Path(__file__).resolve().parents[1]

        self.assertEqual(validate_demo(root), [])


if __name__ == "__main__":
    unittest.main()
