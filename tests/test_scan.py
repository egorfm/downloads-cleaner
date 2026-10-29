from pathlib import Path

from downloads_cleaner.classify import category_for
from downloads_cleaner.scan import extras_from_duplicates, find_duplicates, junk_candidates, scan


def test_categories():
    assert category_for(Path("photo.HEIC")) == "images"
    assert category_for(Path("Setup.dmg")) == "installers"
    assert category_for(Path("file.crdownload")) == "incomplete"
    assert category_for(Path(".DS_Store")) == "junk"


def test_scan_and_duplicates(tmp_path: Path):
    (tmp_path / "a.txt").write_text("same")
    (tmp_path / "copy.txt").write_text("same")
    (tmp_path / "other.txt").write_text("different")
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "video.mp4").write_bytes(b"0" * 32)

    result = scan(tmp_path)
    names = {item.path.name for item in result.files}
    assert names == {"a.txt", "copy.txt", "other.txt", "video.mp4"}
    assert result.by_category()["videos"][0].path.name == "video.mp4"

    groups = find_duplicates(result.files)
    assert len(groups) == 1
    extras = extras_from_duplicates(groups)
    assert len(extras) == 1


def test_junk_picks_incomplete_and_old_installers(tmp_path: Path):
    incomplete = tmp_path / "chrome.crdownload"
    incomplete.write_text("partial")
    installer = tmp_path / "App.dmg"
    installer.write_bytes(b"pkg")
    installer.touch()

    result = scan(tmp_path)
    junk = junk_candidates(result.files, days=0)
    junk_names = {item.path.name for item in junk}
    assert "chrome.crdownload" in junk_names
    assert "App.dmg" in junk_names
