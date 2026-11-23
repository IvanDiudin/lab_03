"""Тесты сущности Route и её инвариантов."""

import pytest

from catalog.errors import CatalogError, InvalidItemError
from catalog.route import Route
from tests.helpers import make_route


def test_valid_route_is_created() -> None:
    route = make_route()
    assert route.item_id == "r1"
    assert route.stops == 18


def test_empty_id_is_rejected() -> None:
    with pytest.raises(InvalidItemError, match="item_id"):
        make_route(item_id="   ")


def test_empty_title_is_rejected() -> None:
    with pytest.raises(InvalidItemError, match="title"):
        make_route(title="")


def test_year_out_of_range_is_rejected() -> None:
    with pytest.raises(InvalidItemError, match="год"):
        make_route(year=3000)


def test_year_as_text_is_rejected() -> None:
    with pytest.raises(InvalidItemError, match="year"):
        make_route(year="1960")  # type: ignore[arg-type]


def test_bool_is_not_a_number_of_stops() -> None:
    with pytest.raises(InvalidItemError, match="stops"):
        make_route(stops=True)  # type: ignore[arg-type]


def test_one_stop_is_rejected() -> None:
    with pytest.raises(InvalidItemError, match="остановок"):
        make_route(stops=1)


def test_zero_duration_is_rejected() -> None:
    with pytest.raises(InvalidItemError, match="больше нуля"):
        make_route(duration_min=0)


def test_route_is_immutable() -> None:
    route = make_route()
    with pytest.raises(AttributeError):
        route.title = "другое"  # type: ignore[misc]


def test_invalid_error_is_catalog_error() -> None:
    with pytest.raises(CatalogError):
        make_route(title="")


def test_to_dict_and_from_dict_are_inverse() -> None:
    route = make_route()
    assert Route.from_dict(route.to_dict()) == route
