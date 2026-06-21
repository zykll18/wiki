from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path


PLATFORM_SLUGS = {
    "豆包": "doubao",
}

HEADER_PATTERN = re.compile(r"^(Title|URL|Platform|Created|Messages):\s*(.*)$")
NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
REQUIRED_HEADERS = {"Title", "URL", "Platform", "Created", "Messages"}


@dataclass
class ImportReport:
    imported: int = 0
    skipped: int = 0
    created_files: list[Path] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)


def parse_headers(text: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in text.splitlines():
        match = HEADER_PATTERN.match(line)
        if not match:
            if headers:
                break
            continue
        headers[match.group(1)] = match.group(2).strip()
    return headers


def looks_like_chat_memo_export(text: str) -> bool:
    headers = parse_headers(text)
    return REQUIRED_HEADERS.issubset(headers)


def slugify(text: str) -> str:
    normalized = NON_ALNUM_PATTERN.sub("-", text.lower()).strip("-")
    return normalized


def platform_slug(platform: str) -> str:
    mapped = PLATFORM_SLUGS.get(platform)
    if mapped:
        return mapped
    slug = slugify(platform)
    return slug or "chat"


def extract_reference_id(url: str, text: str) -> str:
    match = re.search(r"/([A-Za-z0-9]{6,})/?$", url)
    if match:
        return match.group(1)[:8].lower()
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def build_filename(headers: dict[str, str], text: str) -> str:
    created = headers.get("Created", "1970-01-01 00:00:00")
    date_part = created.split()[0]
    title = headers.get("Title", "")
    platform = platform_slug(headers.get("Platform", "chat"))
    title_slug = slugify(title)
    reference_id = extract_reference_id(headers.get("URL", ""), text)

    if title_slug:
        return f"{date_part}-{platform}-{title_slug}-{reference_id}.md"
    return f"{date_part}-{platform}-chat-{reference_id}.md"


def content_digest(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def find_existing_same_url(output_dir: Path, url: str) -> Path | None:
    if not url or not output_dir.exists():
        return None

    for existing_file in sorted(output_dir.glob("*.md")):
        existing_headers = parse_headers(existing_file.read_text(encoding="utf-8"))
        if existing_headers.get("URL") == url:
            return existing_file
    return None


def has_existing_content(output_dir: Path, text: str) -> bool:
    if not output_dir.exists():
        return False
    target_digest = content_digest(text)
    for existing_file in output_dir.glob("*.md"):
        existing_text = existing_file.read_text(encoding="utf-8")
        if content_digest(existing_text) == target_digest:
            return True
    return False


def write_entry(text: str, output_dir: Path, overwrite: bool = False) -> tuple[bool, Path]:
    headers = parse_headers(text)
    filename = build_filename(headers, text)
    destination = output_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    if has_existing_content(output_dir, text):
        return False, destination

    same_url_file = find_existing_same_url(output_dir, headers.get("URL", ""))
    if same_url_file:
        same_url_file.write_text(text, encoding="utf-8")
        return True, same_url_file

    if destination.exists():
        existing = destination.read_text(encoding="utf-8")
        if existing == text or not overwrite:
            return False, destination

    destination.write_text(text, encoding="utf-8")
    return True, destination


def iter_zip_paths(source: Path) -> list[Path]:
    if source.is_dir():
        return sorted(path for path in source.iterdir() if path.suffix.lower() == ".zip")
    return [source]


def import_zip(zip_path: Path, output_dir: Path, overwrite: bool = False) -> ImportReport:
    report = ImportReport()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            if member.endswith("/") or not member.lower().endswith(".txt"):
                continue
            text = archive.read(member).decode("utf-8", errors="replace")
            if not looks_like_chat_memo_export(text):
                report.skipped += 1
                report.skipped_files.append(member)
                continue
            created, destination = write_entry(text, output_dir, overwrite=overwrite)
            if created:
                report.imported += 1
                report.created_files.append(destination)
            else:
                report.skipped += 1
                report.skipped_files.append(member)
    return report


def import_path(source: Path | str, output_dir: Path | str, overwrite: bool = False) -> ImportReport:
    source_path = Path(source)
    output_path = Path(output_dir)
    combined = ImportReport()
    for zip_path in iter_zip_paths(source_path):
        try:
            report = import_zip(zip_path, output_path, overwrite=overwrite)
        except zipfile.BadZipFile:
            combined.skipped += 1
            combined.skipped_files.append(zip_path.name)
            continue
        combined.imported += report.imported
        combined.skipped += report.skipped
        combined.created_files.extend(report.created_files)
        combined.skipped_files.extend(report.skipped_files)
    return combined


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import Chat Memo export zips into raw/conversations markdown files."
    )
    parser.add_argument("source", help="Path to a chat-memo zip or a directory of zip files.")
    parser.add_argument(
        "--output",
        default="raw/conversations",
        help="Output directory for imported markdown files. Defaults to raw/conversations.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files when the destination filename already exists.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    report = import_path(args.source, args.output, overwrite=args.overwrite)

    print(f"Imported: {report.imported}")
    print(f"Skipped: {report.skipped}")
    for path in report.created_files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
