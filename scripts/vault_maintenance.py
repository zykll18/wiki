from __future__ import annotations

import argparse
from dataclasses import dataclass
import re
from pathlib import Path


WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ALLOWED_ROOT_NOTES = {"README.md", "AGENTS.md", "index.md", "log.md"}
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
PLACEHOLDER_WIKILINKS = {"相关 topic 或 synthesis", "来源 A", "来源 B"}
IGNORED_MARKDOWN_DIRS = {
    ".git", ".obsidian", "__pycache__", "node_modules", "capture-pet", "docs", "examples"
}
SYNTHESIS_REQUIRED_SECTION_GROUPS = (
    {"当前判断", "Current Judgment"},
    {"例外与待验证", "Exceptions and Verification"},
    {"相关页面", "Related Pages"},
)
QUERY_WORKFLOW_FILENAMES = ("Query and Writeback Workflow.md", "查询与回写工作流.md")
QUERY_REQUIRED_SECTION_GROUPS = (
    {"当前判断", "Current Judgment"},
    {"回写判定", "Writeback Decision"},
    {"回写模板", "Writeback Template"},
    {"例外与待验证", "Exceptions and Verification"},
    {"相关页面", "Related Pages"},
)


@dataclass
class SynthesisSuggestion:
    path: Path
    score: int


@dataclass
class RewriteCandidate:
    path: Path
    reason: str


@dataclass
class MergeCandidate:
    first: Path
    second: Path
    score: float


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part in IGNORED_MARKDOWN_DIRS for part in path.relative_to(root).parts)
    )


def collect_note_stems(root: Path) -> set[str]:
    return {path.stem.lower() for path in iter_markdown_files(root)}


def iter_wiki_knowledge_pages(root: Path) -> list[Path]:
    wiki_dir = root / "wiki"
    if not wiki_dir.exists():
        return []
    allowed_dirs = {"topics", "syntheses", "entities"}
    return sorted(
        path
        for path in wiki_dir.rglob("*.md")
        if len(path.relative_to(wiki_dir).parts) >= 2 and path.relative_to(wiki_dir).parts[0] in allowed_dirs
    )


def iter_lintable_wiki_pages(root: Path) -> list[Path]:
    wiki_dir = root / "wiki"
    if not wiki_dir.exists():
        return []
    allowed_dirs = {"topics", "syntheses"}
    return sorted(
        path
        for path in wiki_dir.rglob("*.md")
        if len(path.relative_to(wiki_dir).parts) >= 2 and path.relative_to(wiki_dir).parts[0] in allowed_dirs
    )


def extract_wikilinks(text: str) -> list[str]:
    return WIKILINK_PATTERN.findall(text)


def extract_markdown_targets(text: str) -> list[str]:
    return MARKDOWN_LINK_PATTERN.findall(text)


def tokenize_text(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def page_links(path: Path) -> list[str]:
    return extract_wikilinks(path.read_text(encoding="utf-8", errors="replace"))


def lines_outside_code_fences(text: str) -> list[tuple[int, str]]:
    in_fence = False
    result: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append((line_number, line))
    return result


def extract_headings(text: str) -> set[str]:
    return {match.strip() for match in HEADING_PATTERN.findall(text)}


def has_any_link(line: str) -> bool:
    return bool(WIKILINK_PATTERN.search(line) or MARKDOWN_LINK_PATTERN.search(line))


def build_inbound_link_counts(root: Path) -> dict[str, int]:
    counts = {path.stem.lower(): 0 for path in iter_markdown_files(root)}
    for note in iter_markdown_files(root):
        for link in page_links(note):
            key = link.lower()
            if key in counts:
                counts[key] += 1
    return counts


def read_raw_context(raw_file: Path) -> str:
    text = raw_file.read_text(encoding="utf-8", errors="replace")
    headers = []
    body_lines = []
    in_body = False
    for line in text.splitlines():
        if not in_body and line.startswith(("Title:", "URL:", "Platform:", "Created:", "Messages:")):
            headers.append(line)
            continue
        if not line.strip() and headers and not in_body:
            in_body = True
            continue
        if in_body:
            body_lines.append(line)
    if headers:
        return "\n".join(headers + body_lines[:20])
    return "\n".join(text.splitlines()[:25])


def collect_summary_raw_targets(root: Path) -> set[Path]:
    targets: set[Path] = set()
    summaries_dir = root / "wiki" / "summaries"
    if not summaries_dir.exists():
        return targets

    for summary in summaries_dir.glob("*.md"):
        text = summary.read_text(encoding="utf-8")
        for target in extract_markdown_targets(text):
            candidate = Path(target)
            if not candidate.suffix == ".md":
                continue
            if "raw" not in candidate.parts and not target.startswith("raw/"):
                continue
            candidate = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
            targets.add(candidate)
    return targets


def find_pending_raw_files(root: Path | str) -> list[Path]:
    root_path = Path(root).resolve()
    raw_dir = root_path / "raw"
    raw_files = sorted(path.resolve() for path in raw_dir.rglob("*.md")) if raw_dir.exists() else []
    raw_files = [
        path
        for path in raw_files
        if path.relative_to(raw_dir).as_posix() != "inbox/pending.md"
    ]
    referenced = collect_summary_raw_targets(root_path)
    return [path for path in raw_files if path not in referenced]


def find_orphan_pages(root: Path | str) -> list[Path]:
    root_path = Path(root).resolve()
    inbound_counts = build_inbound_link_counts(root_path)
    return [
        path
        for path in iter_wiki_knowledge_pages(root_path)
        if inbound_counts.get(path.stem.lower(), 0) == 0
    ]


def find_weakly_linked_pages(root: Path | str, min_links: int = 2) -> list[Path]:
    root_path = Path(root).resolve()
    weak_pages: list[Path] = []
    for path in iter_wiki_knowledge_pages(root_path):
        unique_links = {link.lower() for link in page_links(path)}
        if len(unique_links) < min_links:
            weak_pages.append(path)
    return weak_pages


def find_rewrite_candidates(root: Path | str, summary_threshold: int = 3) -> list[RewriteCandidate]:
    root_path = Path(root).resolve()
    summary_dir = root_path / "wiki" / "summaries"
    summary_link_counts: dict[str, int] = {}
    if summary_dir.exists():
        for summary in summary_dir.glob("*.md"):
            for link in page_links(summary):
                summary_link_counts[link.lower()] = summary_link_counts.get(link.lower(), 0) + 1

    candidates: list[RewriteCandidate] = []
    for page in iter_wiki_knowledge_pages(root_path):
        count = summary_link_counts.get(page.stem.lower(), 0)
        if count >= summary_threshold:
            candidates.append(RewriteCandidate(page, f"linked by {count} summaries"))
    return candidates


def title_similarity(first: Path, second: Path) -> float:
    first_tokens = tokenize_text(first.stem)
    second_tokens = tokenize_text(second.stem)
    if not first_tokens or not second_tokens:
        return 0.0
    return len(first_tokens & second_tokens) / len(first_tokens | second_tokens)


def find_merge_candidates(root: Path | str, min_score: float = 0.6) -> list[MergeCandidate]:
    root_path = Path(root).resolve()
    pages = iter_wiki_knowledge_pages(root_path)
    candidates: list[MergeCandidate] = []
    for index, first in enumerate(pages):
        for second in pages[index + 1 :]:
            score = title_similarity(first, second)
            if score >= min_score:
                candidates.append(MergeCandidate(first=first, second=second, score=score))
    candidates.sort(key=lambda item: (-item.score, item.first.name, item.second.name))
    return candidates


def suggest_syntheses_for_raw(root: Path | str, raw_file: Path | str, limit: int = 3) -> list[SynthesisSuggestion]:
    root_path = Path(root).resolve()
    raw_path = Path(raw_file).resolve()
    synth_dir = root_path / "wiki" / "syntheses"
    if not synth_dir.exists():
        return []

    raw_tokens = tokenize_text(read_raw_context(raw_path))
    suggestions: list[SynthesisSuggestion] = []
    for synth in sorted(synth_dir.glob("*.md")):
        synth_text = synth.read_text(encoding="utf-8", errors="replace")
        synth_tokens = tokenize_text(synth.stem + "\n" + synth_text)
        score = len(raw_tokens & synth_tokens)
        if score > 0:
            suggestions.append(SynthesisSuggestion(path=synth, score=score))

    suggestions.sort(key=lambda item: (-item.score, item.path.name))
    return suggestions[:limit]


def lint_broken_wikilinks(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    note_stems = collect_note_stems(root_path)
    issues: list[str] = []
    for note in iter_markdown_files(root_path):
        if note.relative_to(root_path).parts[0] == "raw":
            continue
        text = note.read_text(encoding="utf-8")
        for _, line in lines_outside_code_fences(text):
            for link in extract_wikilinks(line):
                if link in PLACEHOLDER_WIKILINKS:
                    continue
                if link.lower() not in note_stems:
                    issues.append(f"{note}: broken wikilink -> [[{link}]]")
    return issues


def lint_summary_raw_targets(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    issues: list[str] = []
    summaries_dir = root_path / "wiki" / "summaries"
    if not summaries_dir.exists():
        return issues

    for summary in summaries_dir.glob("*.md"):
        text = summary.read_text(encoding="utf-8")
        for target in extract_markdown_targets(text):
            candidate = Path(target)
            if not candidate.suffix == ".md":
                continue
            if "raw" not in candidate.parts and not target.startswith("raw/"):
                continue
            candidate = candidate.resolve() if candidate.is_absolute() else (root_path / candidate).resolve()
            if not candidate.exists():
                issues.append(f"{summary}: missing raw target -> {candidate.name}")
    return issues


def lint_unexpected_root_notes(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    issues: list[str] = []
    for note in sorted(root_path.glob("*.md")):
        if note.name not in ALLOWED_ROOT_NOTES:
            issues.append(f"{note}: unexpected root note")
    return issues


def lint_missing_required_sections(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    synth_dir = root_path / "wiki" / "syntheses"
    if not synth_dir.exists():
        return []

    issues: list[str] = []
    for synth in sorted(synth_dir.glob("*.md")):
        headings = extract_headings(synth.read_text(encoding="utf-8", errors="replace"))
        missing = sorted(
            "/".join(sorted(group))
            for group in SYNTHESIS_REQUIRED_SECTION_GROUPS
            if not headings.intersection(group)
        )
        if missing:
            issues.append(f"{synth}: missing required sections -> {', '.join(missing)}")
    return issues


def lint_query_writeback_workflow(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    synth_dir = root_path / "wiki" / "syntheses"
    workflow = next(
        (synth_dir / name for name in QUERY_WORKFLOW_FILENAMES if (synth_dir / name).exists()),
        synth_dir / QUERY_WORKFLOW_FILENAMES[0],
    )
    if not workflow.exists():
        return [f"{workflow}: missing query writeback workflow"]

    headings = extract_headings(workflow.read_text(encoding="utf-8", errors="replace"))
    missing = sorted(
        "/".join(sorted(group))
        for group in QUERY_REQUIRED_SECTION_GROUPS
        if not headings.intersection(group)
    )
    if missing:
        return [f"{workflow}: missing required sections -> {', '.join(missing)}"]
    return []


def lint_unlinked_verification_claims(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    issues: list[str] = []
    for note in iter_lintable_wiki_pages(root_path):
        text = note.read_text(encoding="utf-8", errors="replace")
        for line_number, line in lines_outside_code_fences(text):
            if "待验证" in line and not has_any_link(line) and not line.lstrip().startswith("#"):
                issues.append(f"{note}:{line_number}: verification claim has no source link")
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan pending raw files and lint an Obsidian-style LLM wiki vault."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Vault root directory. Defaults to the current directory.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()

    pending = find_pending_raw_files(root)
    orphan_pages = find_orphan_pages(root)
    weak_pages = find_weakly_linked_pages(root)
    rewrite_candidates = find_rewrite_candidates(root)
    merge_candidates = find_merge_candidates(root)
    lint_issues = []
    lint_issues.extend(lint_broken_wikilinks(root))
    lint_issues.extend(lint_summary_raw_targets(root))
    lint_issues.extend(lint_unexpected_root_notes(root))
    lint_issues.extend(lint_missing_required_sections(root))
    lint_issues.extend(lint_query_writeback_workflow(root))
    lint_issues.extend(lint_unlinked_verification_claims(root))

    print("Pending raw files:")
    if pending:
        for path in pending:
            print(path)
            suggestions = suggest_syntheses_for_raw(root, path)
            if suggestions:
                for suggestion in suggestions:
                    print(f"  -> maybe update: {suggestion.path.name} (score={suggestion.score})")
    else:
        print("None")

    print("\nRewrite candidates:")
    if rewrite_candidates:
        for candidate in rewrite_candidates:
            print(f"{candidate.path} ({candidate.reason})")
    else:
        print("None")

    print("\nOrphan pages:")
    if orphan_pages:
        for path in orphan_pages:
            print(path)
    else:
        print("None")

    print("\nWeakly linked pages:")
    if weak_pages:
        for path in weak_pages:
            print(path)
    else:
        print("None")

    print("\nMerge candidates:")
    if merge_candidates:
        for candidate in merge_candidates:
            print(f"{candidate.first} <-> {candidate.second} (score={candidate.score:.2f})")
    else:
        print("None")

    print("\nLint issues:")
    if lint_issues:
        for issue in lint_issues:
            print(issue)
    else:
        print("None")

    return 1 if lint_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
