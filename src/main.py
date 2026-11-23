"""Точка входа в приложение."""

from catalog.catalog import Catalog
from catalog.route import Route


def main() -> None:
    """Демонстрация работы каталога."""
    print("Запуск каталога транспортных маршрутов...")
    catalog = Catalog()

    route = Route(
        item_id="r1",
        title="Вокзал - Парк",
        category="автобус",
        year=1960,
        stops=18,
        duration_min=45,
    )

    catalog.add(route)
    print(f"Успешно добавлен маршрут: {catalog.get('r1').title}")
    print(f"Всего маршрутов: {len(catalog)}")


if __name__ == "__main__":
    main()
