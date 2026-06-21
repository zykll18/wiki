from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_DIR = Path(
    os.environ.get("LAST30DAYS_SKILL_DIR", Path.home() / ".agents" / "skills" / "last30days")
)
DEFAULT_SAVE_DIR = REPOSITORY_ROOT / "raw" / "search" / "last30days"
DEFAULT_SOURCES = "reddit,hackernews,polymarket,github,youtube"
CLUSTER_PATTERN = re.compile(
    r"^###\s+(?P<rank>\d+)\.\s+(?P<title>.+?)\s+\(score\s+(?P<score>-?\d+),.*?sources:\s+(?P<sources>[^)]+)\)",
    re.MULTILINE,
)
SOURCE_COVERAGE_PATTERN = re.compile(r"^-\s+([^:]+):\s+(\d+)\s+items?", re.MULTILINE)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "last30days"


def escape_table_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def markdown_link(label: object, url: object) -> str:
    text = escape_table_cell(label) or "Untitled"
    href = str(url or "").strip()
    if not href:
        return text
    return f"[{text}]({href})"


def append_pending(root: Path, path: Path) -> Path:
    pending_path = root / "raw" / "inbox" / "pending.md"
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    if not pending_path.exists():
        pending_path.write_text("# Pending Inbox\n\n", encoding="utf-8")

    relative_path = path.relative_to(root).as_posix()
    line = f"- [ ] {relative_path}\n"
    existing = pending_path.read_text(encoding="utf-8")
    if line not in existing:
        with pending_path.open("a", encoding="utf-8") as pending:
            pending.write(line)
    return pending_path


def newest_markdown_after(directory: Path, started_at: float) -> Path | None:
    candidates = [
        path
        for path in directory.glob("*.md")
        if path.stat().st_mtime >= started_at - 1
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def extract_first_match(block: str, pattern: str) -> str:
    match = re.search(pattern, block, re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_ranked_clusters(text: str, limit: int = 8) -> list[dict[str, str]]:
    matches = list(CLUSTER_PATTERN.finditer(text))
    clusters: list[dict[str, str]] = []
    for index, match in enumerate(matches[:limit]):
        block_start = match.end()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[block_start:block_end]
        meta = extract_first_match(block, r"^\s+-\s+(\d{4}-\d{2}-\d{2}\s+\|\s+.+)$")
        meta_parts = [part.strip() for part in meta.split("|")] if meta else []
        clusters.append(
            {
                "rank": match.group("rank"),
                "title": match.group("title"),
                "score": match.group("score"),
                "sources": match.group("sources"),
                "url": extract_first_match(block, r"^\s+-\s+URL:\s+(.+)$"),
                "date": meta_parts[0] if len(meta_parts) >= 1 else "",
                "voice": meta_parts[1] if len(meta_parts) >= 2 else "",
            }
        )
    return clusters


def parse_source_coverage(text: str) -> list[tuple[str, str]]:
    marker = "## Source Coverage"
    if marker not in text:
        return []
    section = text.split(marker, 1)[1]
    next_section = re.search(r"\n##\s+", section)
    if next_section:
        section = section[: next_section.start()]
    return [(source.strip(), count.strip()) for source, count in SOURCE_COVERAGE_PATTERN.findall(section)]


def render_last30days_overview(text: str) -> str:
    if "\n## 结果概览\n" in text:
        return ""

    clusters = parse_ranked_clusters(text)
    coverage = parse_source_coverage(text)
    if not clusters and not coverage:
        return ""

    lines = [
        "## 结果概览",
        "",
    ]
    if clusters:
        lines.extend(
            [
                "| # | 标题 | 来源 | 分数 | 日期 | 作者/社区 |",
                "|---|---|---|---:|---|---|",
            ]
        )
        for cluster in clusters:
            lines.append(
                "| {rank} | {title} | {sources} | {score} | {date} | {voice} |".format(
                    rank=escape_table_cell(cluster["rank"]),
                    title=markdown_link(cluster["title"], cluster["url"]),
                    sources=escape_table_cell(cluster["sources"]),
                    score=escape_table_cell(cluster["score"]),
                    date=escape_table_cell(cluster["date"]),
                    voice=escape_table_cell(cluster["voice"]),
                )
            )
    else:
        lines.append("未解析到 ranked clusters，请查看下方原始输出。")

    if coverage:
        lines.extend(
            [
                "",
                "## 来源覆盖",
                "",
                "| 来源 | 条目数 |",
                "|---|---:|",
            ]
        )
        for source, count in coverage:
            lines.append(f"| {escape_table_cell(source)} | {escape_table_cell(count)} |")

    lines.extend(
        [
            "",
            "## 使用限制",
            "",
            "- 这是外国社区搜源结果，只能作为社区信号，不直接当事实结论。",
            "- 分数代表工具排序，不代表来源可信度。",
            "- 如果 X、GitHub、YouTube transcript 等来源为 0 或 degraded，需要单独补搜或提高配置。",
            "",
        ]
    )
    return "\n".join(lines)


def render_diagnostics_section(stderr: str) -> str:
    text = stderr.strip()
    if not text:
        return ""

    lines: list[str] = []
    if re.search(r"Bird error: Search timed out|Search timed out after", text, re.IGNORECASE):
        lines.append("- X/Bird 搜索超时：认证有效不等于搜索稳定，当前请求没有在后端超时时间内返回。可重试 `--depth deep`，或改用更稳定的 X 官方/API 后端。")
    if re.search(r"Bird error: Bird search failed", text, re.IGNORECASE):
        lines.append("- X/Bird 后端搜索失败：这不是关键词无结果，而是当前 Bird 搜索请求失败。可稍后重试，或改用 X 官方/API 后端。")
    if re.search(r"No GitHub token available|gh auth login|not logged into any GitHub", text, re.IGNORECASE):
        lines.append("- GitHub 未认证：需要先执行 `gh auth login`，或设置 `GITHUB_TOKEN`，否则 GitHub 来源会是 0。")
    if re.search(r"Permission denied reading Cookies\.binarycookies|Full Disk Access", text, re.IGNORECASE):
        lines.append("- 浏览器 Cookie 读取权限不足：macOS 阻止读取 Safari Cookie；如果要走浏览器 Cookie，需要给 Terminal/Codex Full Disk Access，或继续使用已写入的 X token。")
    if re.search(r"403|forbidden", text, re.IGNORECASE):
        lines.append("- 有来源返回 403：通常是匿名访问受限、频率限制或登录状态失效，需要单独处理该来源。")
    if re.search(r"transcript", text, re.IGNORECASE):
        lines.append("- 视频 transcript 来源不完整：这只影响视频正文理解，不代表视频搜索本身失败。")

    if not lines:
        lines.append("- 工具有 stderr 输出，但没有匹配到已知错误类型；保留原始诊断供后续排查。")

    lines.extend(
        [
            "",
            "<details>",
            "<summary>原始诊断</summary>",
            "",
            "```text",
            text,
            "```",
            "</details>",
            "",
        ]
    )
    return "\n".join(["## 抓取诊断", "", *lines])


def enhance_saved_markdown(path: Path, stderr: str = "") -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    overview = render_last30days_overview(text)
    diagnostics = "" if "\n## 抓取诊断\n" in text else render_diagnostics_section(stderr)
    if not overview and not diagnostics:
        return
    lines = text.splitlines()
    insert_at = 1
    # Keep the title first, then place the human-facing overview before raw tool sections.
    inserts = [block.rstrip() for block in (overview, diagnostics) if block]
    enhanced = "\n".join(lines[:insert_at] + ["", "\n\n".join(inserts), ""] + lines[insert_at:]) + "\n"
    path.write_text(enhanced, encoding="utf-8")


def resolve_depth(args: argparse.Namespace) -> str:
    if args.depth:
        return args.depth
    return "quick" if args.quick else "default"


def build_last30days_command(args: argparse.Namespace, script: Path, save_dir: Path) -> list[str]:
    command = [
        sys.executable,
        str(script),
        args.topic,
        "--emit",
        args.emit,
        "--save-dir",
        str(save_dir),
        "--days",
        str(args.days),
        "--search",
        args.sources,
        "--web-backend",
        args.web_backend,
    ]
    depth = resolve_depth(args)
    if depth == "quick":
        command.append("--quick")
    elif depth == "deep":
        command.append("--deep")
    if args.debug:
        command.append("--debug")
    if args.save_suffix:
        command.extend(["--save-suffix", args.save_suffix])
    return command


def run_search(args: argparse.Namespace, root: Path = REPOSITORY_ROOT) -> Path:
    skill_dir = Path(args.skill_dir).expanduser().resolve()
    script = skill_dir / "scripts" / "last30days.py"
    if not script.exists():
        raise SystemExit(f"last30days script not found: {script}")

    save_dir = Path(args.save_dir).expanduser().resolve()
    save_dir.mkdir(parents=True, exist_ok=True)

    command = build_last30days_command(args, script, save_dir)

    started_at = time.time()
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)

    output_file = newest_markdown_after(save_dir, started_at)
    if output_file is None:
        output_file = save_dir / f"{time.strftime('%Y-%m-%d')}-{slugify(args.topic)}-last30days.md"
        output_file.write_text(
            "\n".join(
                [
                    f"# last30days search - {args.topic}",
                    "",
                    "## stdout",
                    "```text",
                    completed.stdout.strip(),
                    "```",
                    "",
                    "## stderr",
                    "```text",
                    completed.stderr.strip(),
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    enhance_saved_markdown(output_file, completed.stderr)
    pending_path = append_pending(root, output_file)
    print(f"Saved: {output_file}")
    print(f"Pending: {pending_path}")
    if completed.stderr.strip():
        print("\nDiagnostics:")
        print(completed.stderr.strip())
    return output_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run last30days and save the raw result into this LLM wiki vault."
    )
    parser.add_argument("topic", help="Research topic, e.g. 'Agent Skill negative transfer'.")
    parser.add_argument(
        "--skill-dir",
        default=str(DEFAULT_SKILL_DIR),
        help="Path to installed last30days skill.",
    )
    parser.add_argument(
        "--save-dir",
        default=str(DEFAULT_SAVE_DIR),
        help="Where raw last30days files are saved.",
    )
    parser.add_argument(
        "--sources",
        default=DEFAULT_SOURCES,
        help="Comma-separated source list.",
    )
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days.")
    parser.add_argument(
        "--emit",
        choices=["compact", "md", "json", "context", "html"],
        default="md",
    )
    parser.add_argument(
        "--web-backend",
        choices=["auto", "brave", "exa", "serper", "parallel", "none"],
        default="none",
    )
    parser.add_argument("--save-suffix", default="", help="Optional suffix for last30days raw output.")
    parser.add_argument(
        "--depth",
        choices=["quick", "default", "deep"],
        default=None,
        help="Retrieval depth. quick is fastest; deep gives slow sources like X more time.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Pass debug mode through to last30days.",
    )
    parser.add_argument(
        "--quick",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Backward-compatible shortcut. Ignored when --depth is set.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    run_search(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
