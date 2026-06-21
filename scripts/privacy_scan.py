from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


IGNORED_PARTS = {".git", "node_modules", "dist", "__pycache__"}
IGNORED_PREFIXES = (Path("docs/superpowers"),)
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
PATTERNS = {
    "secret": re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{8,}|gh[oprsu]_[A-Za-z0-9]{20,}|"
        r"as_sk_[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._~+/-]{12,})\b"
    ),
    "absolute-user-path": re.compile(r"/" + r"Users/[A-Za-z0-9._-]+/"),
    "email": re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    kind: str
    excerpt: str


def iter_text_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
        and not any(
            path.relative_to(root).is_relative_to(prefix)
            for prefix in IGNORED_PREFIXES
        )
    )


def scan_repository(root: Path | str) -> list[Finding]:
    root_path = Path(root).resolve()
    findings: list[Finding] = []
    private_journal = root_path / "raw" / "projects"
    if private_journal.exists():
        findings.append(
            Finding(
                path=private_journal.relative_to(root_path),
                line=0,
                kind="private-journal-path",
                excerpt="private journal directory exists",
            )
        )

    for path in iter_text_files(root_path):
        if path.name == ".env.example":
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, start=1):
            for kind, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=path.relative_to(root_path),
                            line=number,
                            kind=kind,
                            excerpt=pattern.sub("[REDACTED]", line)[:200],
                        )
                    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan the public repository for private data."
    )
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    findings = scan_repository(args.root)
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.kind}: {finding.excerpt}")
    print(f"Privacy findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
