from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from downloads_cleaner.classify import category_for

SKIP_DIR_NAMES = {".git", ".Trash", "node_modules"}
CHUNK = 1024 * 1024


@dataclass
class FileInfo:
    path: Path
    size: int
    mtime: float
    category: str

    @property
    def age_days(self) -> int:
        return max(0, int((datetime.now().timestamp() - self.mtime) / 86400))


@dataclass
class ScanResult:
    root: Path
    files: list[FileInfo] = field(default_factory=list)

    def by_category(self) -> dict[str, list[FileInfo]]:
        groups: dict[str, list[FileInfo]] = defaultdict(list)
        for item in self.files:
            groups[item.category].append(item)
        return dict(groups)

    def older_than(self, days: int) -> list[FileInfo]:
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_ts = cutoff.timestamp()
        return [item for item in self.files if item.mtime < cutoff_ts]


def default_downloads() -> Path:
    return Path.home() / "Downloads"


def _is_skipped(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(part in SKIP_DIR_NAMES for part in parts)


def iter_files(root: Path) -> list[FileInfo]:
    files: list[FileInfo] = []
    for path in root.rglob("*"):
        if _is_skipped(path, root):
            continue
        if path.is_dir():
            continue
        if not path.is_file() or path.is_symlink():
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        files.append(
            FileInfo(
                path=path,
                size=stat.st_size,
                mtime=stat.st_mtime,
                category=category_for(path),
            )
        )
    return files


def scan(root: Path) -> ScanResult:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")
    files = iter_files(root)
    return ScanResult(root=root, files=files)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(files: list[FileInfo]) -> list[list[FileInfo]]:
    by_size: dict[int, list[FileInfo]] = defaultdict(list)
    for item in files:
        if item.size == 0:
            continue
        by_size[item.size].append(item)

    groups: list[list[FileInfo]] = []
    for candidates in by_size.values():
        if len(candidates) < 2:
            continue
        by_hash: dict[str, list[FileInfo]] = defaultdict(list)
        for item in candidates:
            try:
                by_hash[file_hash(item.path)].append(item)
            except OSError:
                continue
        for hashed in by_hash.values():
            if len(hashed) > 1:
                hashed.sort(key=lambda item: item.mtime, reverse=True)
                groups.append(hashed)
    groups.sort(key=lambda group: group[0].size * (len(group) - 1), reverse=True)
    return groups


def junk_candidates(files: list[FileInfo], days: int) -> list[FileInfo]:
    old = {item.path for item in ScanResult(Path("."), files).older_than(days)}
    picked: list[FileInfo] = []
    for item in files:
        if item.category in {"incomplete", "junk"}:
            picked.append(item)
        elif item.category == "installers" and item.path in old:
            picked.append(item)
    picked.sort(key=lambda item: item.mtime)
    return picked


def extras_from_duplicates(groups: list[list[FileInfo]]) -> list[FileInfo]:
    extras: list[FileInfo] = []
    for group in groups:
        extras.extend(group[1:])
    return extras
