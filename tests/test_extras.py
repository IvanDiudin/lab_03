"""Тесты дополнительных заданий: индекс, read-only view, миграция v1."""

import json
from pathlib import Path

import pytest

from catalog.catalog import Catalog, CatalogView
from catalog.errors import CorruptedFileError
from catalog.storage import load_catalog, save_catalog
from tests.helpers import make_route


def linear_by_category(catalog: Catalog, category: str) -> list[str]:
    """Эталон без индекса: перебираем все маршруты."""
    return [route.item_id for route in catalog if route.category == category]


def test_index_matches_linear_search_after_operations() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1", category="автобус"))
    catalog.add(make_route("r2", category="трамвай"))
    catalog.add(make_route("r3", category="автобус"))
    catalog.remove("r1")
    catalog.add(make_route("r4", category="автобус"))
    got = [route.item_id for route in catalog.find_by_category("автобус")]
    assert got == linear_by_category(catalog, "автобус") == ["r3", "r4"]


def test_empty_category_is_removed_from_index() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1", category="метро"))
    catalog.remove("r1")
    assert catalog.find_by_category("метро") == ()
    assert "метро" not in catalog._by_category


def test_index_is_rebuilt_after_load(tmp_path: Path) -> None:
    source = Catalog()
    source.add(make_route("r1", category="трамвай"))
    source.add(make_route("r2", category="трамвай"))
    path = str(tmp_path / "c.json")
    save_catalog(source, path)

    target = Catalog()
    target.add(make_route("old", category="метро"))
    load_catalog(target, path)
    assert [r.item_id for r in target.find_by_category("трамвай")] == ["r1", "r2"]
    assert target.find_by_category("метро") == ()


def test_view_has_no_write_methods() -> None:
    view = CatalogView(Catalog())
    assert not hasattr(view, "add")
    assert not hasattr(view, "remove")
    assert not hasattr(view, "replace_all")


def test_view_reads_live_catalog() -> None:
    catalog = Catalog()
    view = CatalogView(catalog)
    catalog.add(make_route("r1", title="Вокзал - Парк"))
    assert "r1" in view
    assert view.get("r1").title == "Вокзал - Парк"
    assert len(view) == 1


def test_v1_document_is_migrated(tmp_path: Path) -> None:
    v1_item = {
        "item_id": "r1",
        "title": "Вокзал - Парк",
        "category": "автобус",
        "date": "1960",
        "stops": 18,
        "duration_min": 45,
    }
    path = tmp_path / "v1.json"
    path.write_text(
        json.dumps({"format_version": 1, "items": [v1_item]}, ensure_ascii=False),
        encoding="utf-8",
    )
    catalog = Catalog()
    load_catalog(catalog, str(path))
    assert catalog.get("r1").year == 1960


def test_v1_with_bad_year_is_corruption_and_keeps_catalog(tmp_path: Path) -> None:
    catalog = Catalog()
    catalog.add(make_route("keep"))
    bad = {
        "item_id": "r1",
        "title": "x",
        "category": "автобус",
        "date": "не-год",
        "stops": 5,
        "duration_min": 10,
    }
    path = tmp_path / "v1bad.json"
    path.write_text(json.dumps({"format_version": 1, "items": [bad]}), encoding="utf-8")
    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, str(path))
    assert "keep" in catalog
    assert len(catalog) == 1
