from pathlib import Path

CATEGORIES: dict[str, set[str]] = {
    "images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic",
        ".heif",
        ".bmp",
        ".svg",
        ".tif",
        ".tiff",
        ".raw",
        ".cr2",
        ".nef",
    },
    "videos": {
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".m4v",
        ".wmv",
        ".flv",
    },
    "audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma", ".aiff"},
    "documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".rtf",
        ".odt",
        ".ods",
        ".csv",
        ".md",
        ".pages",
        ".numbers",
        ".key",
        ".epub",
    },
    "archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz"},
    "installers": {
        ".dmg",
        ".pkg",
        ".exe",
        ".msi",
        ".apk",
        ".ipa",
        ".appimage",
        ".deb",
        ".rpm",
    },
    "code": {
        ".py",
        ".js",
        ".ts",
        ".json",
        ".yml",
        ".yaml",
        ".xml",
        ".html",
        ".css",
        ".ipynb",
        ".sh",
        ".sql",
    },
    "incomplete": {
        ".crdownload",
        ".part",
        ".partial",
        ".download",
        ".tmp",
        ".temp",
    },
}

JUNK_NAMES = {
    ".ds_store",
    "thumbs.db",
    "desktop.ini",
    ".localized",
}


def category_for(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    if name in JUNK_NAMES:
        return "junk"
    if suffix in CATEGORIES["incomplete"] or name.endswith(".download"):
        return "incomplete"
    for category, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return category
    return "other"
