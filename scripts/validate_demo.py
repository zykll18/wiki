from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_GLOBS = {
    "missing raw sources": "raw/**/*.md",
    "missing summaries": "wiki/summaries/*.md",
    "missing topic": "wiki/topics/*.md",
    "missing entity": "wiki/entities/*.md",
    "missing synthesis": "wiki/syntheses/*.md",
}
DECISION_FIELDS = (
    "Primary topic",
    "Retention reason",
    "Excluded content",
    "Final storage layer",
    "Source reliability",
    "Verification boundary",
)


def validate_demo(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    issues = [
        label
        for label, pattern in REQUIRED_GLOBS.items()
        if not list(root_path.glob(pattern))
    ]
    summary_dir = root_path / "wiki" / "summaries"
    if summary_dir.exists():
        for summary in sorted(summary_dir.glob("*.md")):
            text = summary.read_text(encoding="utf-8")
            for field in DECISION_FIELDS:
                if field not in text:
                    issues.append(f"{summary.name}: missing {field}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the published demo knowledge flow.")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    issues = validate_demo(args.root)
    for issue in issues:
        print(issue)
    print(f"Demo validation issues: {len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
