from __future__ import annotations

import argparse
import sys
from pathlib import Path

from send2trash import send2trash

from downloads_cleaner.report import render_report
from downloads_cleaner.scan import (
    extras_from_duplicates,
    find_duplicates,
    junk_candidates,
    scan,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="downloads-cleaner",
        description="Look through Downloads, group files, and optionally trash junk and duplicates.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(Path.home() / "Downloads"),
        help="folder to scan (default: ~/Downloads)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="treat files older than this as stale (default: 30)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="move selected files to Trash (default is a dry run)",
    )
    parser.add_argument(
        "--junk",
        action="store_true",
        help="include incomplete files, junk, and old installers",
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="include extra copies (keeps the newest file in each group)",
    )
    parser.add_argument(
        "--old",
        action="store_true",
        help="include everything older than --days (be careful)",
    )
    return parser


def targets_for(result, days: int, junk: bool, duplicates: bool, old: bool) -> list:
    seen: set[Path] = set()
    picked = []

    buckets = []
    if junk:
        buckets.append(junk_candidates(result.files, days))
    if duplicates:
        buckets.append(extras_from_duplicates(find_duplicates(result.files)))
    if old:
        buckets.append(result.older_than(days))

    for bucket in buckets:
        for item in bucket:
            if item.path in seen:
                continue
            seen.add(item.path)
            picked.append(item)
    picked.sort(key=lambda item: str(item.path))
    return picked


def trash_files(files) -> tuple[int, int]:
    ok = 0
    failed = 0
    for item in files:
        try:
            send2trash(str(item.path))
            ok += 1
        except OSError as exc:
            print(f"could not trash {item.path}: {exc}", file=sys.stderr)
            failed += 1
    return ok, failed


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.path)

    try:
        result = scan(root)
    except (NotADirectoryError, FileNotFoundError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(render_report(result, args.days), end="")

    selected = args.junk or args.duplicates or args.old
    if not selected:
        print("Dry run only. Pass --junk / --duplicates / --old plus --apply to trash files.")
        return 0

    files = targets_for(result, args.days, args.junk, args.duplicates, args.old)
    print()
    print(f"Selected {len(files)} file(s) to trash.")
    for item in files[:30]:
        print(f"  {item.path}")
    if len(files) > 30:
        print(f"  ... and {len(files) - 30} more")

    if not files:
        return 0

    if not args.apply:
        print()
        print("Nothing was moved. Add --apply to send these to Trash.")
        return 0

    ok, failed = trash_files(files)
    print()
    print(f"Moved {ok} file(s) to Trash.")
    if failed:
        print(f"Failed: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
