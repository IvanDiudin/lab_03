"""Тесты сохранения, загрузки, версии формата и атомарности."""

import json
from pathlib import Path

import pytest

from catalog.catalog import Catalog
from catalog.errors import CorruptedFileError, UnsupportedVersionError
from catalog.storage import load_catalog, save_catalog
from tests.helpers import make_route


def write_text(folder: Path, name: str, text: str) -> str:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_round_trip_keeps_all_fields(tmp_path: Path) -> None:
    catalog = Catalog()
    catalog.add(
        make_route(
            "r1",
            title="Центр - Аэропорт",
            category="троллейбус",
            year=1985,
            stops=24,
            duration_min=70,
        )
    )
    path = str(tmp_path / "routes.json")
    save_catalog(catalog, path)

    restored = Catalog()
    load_catalog(restored, path)
    assert list(restored) == list(catalog)


def test_saved_document_has_format_version(tmp_path: Path) -> None:
    path = str(tmp_path / "routes.json")
    save_catalog(Catalog(), path)
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    assert document["format_version"] == 2


def test_unknown_version_is_rejected(tmp_path: Path) -> None:
    path = write_text(
        tmp_path, "v99.json", json.dumps({"format_version": 99, "items": []})
    )
    with pytest.raises(UnsupportedVersionError, match="99"):
        load_catalog(Catalog(), path)


def test_broken_json_is_rejected(tmp_path: Path) -> None:
    path = write_text(tmp_path, "broken.json", "{не json")
    with pytest.raises(CorruptedFileError):
        load_catalog(Catalog(), path)


def test_missing_field_in_item_is_corruption(tmp_path: Path) -> None:
    document = {
        "format_version": 2,
        "items": [
            {
                "item_id": "r1",
                "title": "x",
                "category": "автобус",
                "year": 2000,
                "stops": 5,
            }
        ],
    }
    path = write_text(tmp_path, "nodur.json", json.dumps(document))
    with pytest.raises(CorruptedFileError, match="duration_min"):
        load_catalog(Catalog(), path)


def test_partially_corrupted_file_does_not_change_catalog(tmp_path: Path) -> None:
    """Первый маршрут верный, второй - нет. Каталог должен остаться прежним."""
    catalog = Catalog()
    catalog.add(make_route("old", title="Старый маршрут"))

    good = make_route("new1").to_dict()
    bad = make_route("new2").to_dict()
    bad["duration_min"] = -5
    document = {"format_version": 2, "items": [good, bad]}
    path = write_text(tmp_path, "partial.json", json.dumps(document))

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)
    assert len(catalog) == 1
    assert catalog.get("old").title == "Старый маршрут"
    assert "new1" not in catalog


def test_duplicate_id_in_file_is_corruption(tmp_path: Path) -> None:
    catalog = Catalog()
    catalog.add(make_route("keep"))
    dup = [make_route("same").to_dict(), make_route("same").to_dict()]
    path = write_text(
        tmp_path, "dup.json", json.dumps({"format_version": 2, "items": dup})
    )
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)
    assert "keep" in catalog


def test_missing_title_in_second_item_keeps_catalog(tmp_path: Path) -> None:
    catalog = Catalog()
    catalog.add(make_route("old"))
    good = make_route("new1").to_dict()
    bad = make_route("new2").to_dict()
    del bad["title"]
    path = write_text(
        tmp_path, "p.json", json.dumps({"format_version": 2, "items": [good, bad]})
    )
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)
    assert "old" in catalog and "new1" not in catalog
