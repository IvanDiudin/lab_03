"""Общие данные для тестов."""

from catalog.route import Route


def make_route(
    item_id: str = "r1",
    title: str = "Вокзал - Парк",
    category: str = "автобус",
    year: int = 1960,
    stops: int = 18,
    duration_min: int = 45,
) -> Route:
    """Создаёт корректный маршрут. Параметры можно переопределить."""
    return Route(
        item_id=item_id,
        title=title,
        category=category,
        year=year,
        stops=stops,
        duration_min=duration_min,
    )
