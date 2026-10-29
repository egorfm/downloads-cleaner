from __future__ import annotations

from collections import defaultdict

from downloads_cleaner.scan import FileInfo, ScanResult, find_duplicates, junk_candidates


def _human_size(num: int) -> str:
    value = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{num} B"


def _total_size(files: list[FileInfo]) -> int:
    return sum(item.size for item in files)


def render_report(result: ScanResult, days: int) -> str:
    lines: list[str] = []
    lines.append(f"Folder: {result.root}")
    lines.append(f"Files:  {len(result.files)} ({_human_size(_total_size(result.files))})")
    lines.append("")
    lines.append("By type")
    lines.append("-------")
    grouped = result.by_category()
    for category in sorted(grouped, key=lambda name: _total_size(grouped[name]), reverse=True):
        items = grouped[category]
        lines.append(
            f"  {category:<12} {len(items):>5} files   {_human_size(_total_size(items))}"
        )

    old = result.older_than(days)
    lines.append("")
    lines.append(f"Older than {days} days")
    lines.append("-------------------")
    if not old:
        lines.append("  nothing")
    else:
        by_cat: dict[str, list[FileInfo]] = defaultdict(list)
        for item in old:
            by_cat[item.category].append(item)
        lines.append(f"  {len(old)} files, {_human_size(_total_size(old))}")
        for category in sorted(by_cat):
            items = by_cat[category]
            lines.append(
                f"    {category:<12} {len(items):>4}   {_human_size(_total_size(items))}"
            )

    junk = junk_candidates(result.files, days)
    lines.append("")
    lines.append("Likely junk")
    lines.append("-----------")
    lines.append("  incomplete downloads, leftover junk files,")
    lines.append(f"  and installers older than {days} days")
    if not junk:
        lines.append("  nothing")
    else:
        lines.append(f"  {len(junk)} files, {_human_size(_total_size(junk))}")
        for item in junk[:15]:
            lines.append(f"    {item.path.name}  ({_human_size(item.size)}, {item.age_days}d)")
        if len(junk) > 15:
            lines.append(f"    ... and {len(junk) - 15} more")

    dupes = find_duplicates(result.files)
    lines.append("")
    lines.append("Duplicates")
    lines.append("----------")
    if not dupes:
        lines.append("  nothing")
    else:
        extra = sum(len(group) - 1 for group in dupes)
        extra_size = sum(item.size for group in dupes for item in group[1:])
        lines.append(f"  {len(dupes)} groups, {extra} extra files, {_human_size(extra_size)}")
        for group in dupes[:8]:
            keep = group[0]
            lines.append(f"    keep {keep.path.name} ({_human_size(keep.size)})")
            for extra_file in group[1:]:
                lines.append(f"      dup {extra_file.path}")
        if len(dupes) > 8:
            lines.append(f"    ... and {len(dupes) - 8} more groups")

    return "\n".join(lines) + "\n"
