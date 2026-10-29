# downloads-cleaner

Small CLI that looks at a Downloads folder (or any other directory), groups files by type, and points out the usual mess: leftover `.crdownload` files, old installers, and exact duplicates.

By default it only prints a report. Nothing is deleted. With `--apply` it sends selected files to Trash, not to `/dev/null`.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# report for ~/Downloads
downloads-cleaner

# another folder, treat files older than 14 days as stale
downloads-cleaner ~/Desktop --days 14

# preview what would go to Trash
downloads-cleaner --junk --duplicates

# actually move those files to Trash
downloads-cleaner --junk --duplicates --apply
```

Flags:

- `--junk` — incomplete downloads, junk files (`.DS_Store`, `Thumbs.db`), installers older than `--days`
- `--duplicates` — extra copies; keeps the newest file in each hash group
- `--old` — everything older than `--days` (this one is aggressive, preview first)
- `--apply` — send the selected files to Trash

## Tests

```bash
pip install -e ".[dev]"
pytest
```
