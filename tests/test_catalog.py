"""Тесты каталога маршрутов: добавление, получение, удаление, поиск, протоколы."""

import pytest

from catalog.catalog import Catalog
from catalog.errors import DuplicateIdError, ItemNotFoundError
from tests.helpers import make_route


def test_add_and_get() -> None:
    catalog = Catalog()
    route = make_route("r1")
    catalog.add(route)
    assert catalog.get("r1") == route


def test_remove_deletes_route() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1"))
    catalog.remove("r1")
    assert len(catalog) == 0
    assert "r1" not in catalog


def test_remove_missing_id_is_domain_error() -> None:
    catalog = Catalog()
    with pytest.raises(ItemNotFoundError):
        catalog.remove("нет-такого")


def test_get_missing_id_is_domain_error() -> None:
    catalog = Catalog()
    with pytest.raises(ItemNotFoundError):
        catalog.get("нет-такого")


def test_duplicate_id_is_rejected() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1", title="первый"))
    with pytest.raises(DuplicateIdError):
        catalog.add(make_route("r1", title="второй"))
    assert catalog.get("r1").title == "первый"


def test_find_by_category() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1", category="автобус"))
    catalog.add(make_route("r2", category="трамвай"))
    catalog.add(make_route("r3", category="автобус"))
    found = catalog.find_by_category("автобус")
    assert [route.item_id for route in found] == ["r1", "r3"]


def test_find_by_name_ignores_case() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1", title="Вокзал - Парк"))
    catalog.add(make_route("r2", title="Центр - Аэропорт"))
    found = catalog.find_by_name("ВОКЗАЛ")
    assert [route.item_id for route in found] == ["r1"]


def test_search_returns_tuple_not_internal_list() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1"))
    found = catalog.find_by_name("вокзал")
    assert isinstance(found, tuple)
    with pytest.raises(TypeError):
        found[0] = make_route("r9")  # type: ignore[index]


def test_iteration_order_is_by_id_and_repeatable() -> None:
    catalog = Catalog()
    catalog.add(make_route("c3"))
    catalog.add(make_route("a1"))
    catalog.add(make_route("b2"))
    first = [route.item_id for route in catalog]
    second = [route.item_id for route in catalog]
    assert first == ["a1", "b2", "c3"]
    assert first == second


def test_len_and_contains() -> None:
    catalog = Catalog()
    catalog.add(make_route("r1"))
    assert len(catalog) == 1
    assert "r1" in catalog
    assert "r2" not in catalog
