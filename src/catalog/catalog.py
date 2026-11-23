"""Каталог маршрутов.

Хранение: словарь item_id -> Route. Поиск по номеру делается через словарь,
поэтому не перебирает все маршруты.
Дополнительно: неуникальный индекс category -> множество ID (доп. задание +3).
Порядок итерации: по возрастанию item_id (документировано и детерминировано).
"""

from collections.abc import Iterator

from catalog.errors import DuplicateIdError, ItemNotFoundError
from catalog.route import Route


def sort_key(route: Route) -> str:
    """Ключ сортировки: номер маршрута."""
    return route.item_id


class Catalog:
    """Каталог маршрутов."""

    def __init__(self) -> None:
        self._items: dict[str, Route] = {}
        # Индекс по виду транспорта. Один вид - много маршрутов (неуникальный индекс).
        self._by_category: dict[str, set[str]] = {}

    def add(self, item: Route) -> None:
        """Добавляет маршрут. Повторный номер запрещён."""
        if item.item_id in self._items:
            raise DuplicateIdError(f"маршрут '{item.item_id}' уже есть в каталоге")
        self._items[item.item_id] = item
        self._by_category.setdefault(item.category, set()).add(item.item_id)

    def get(self, item_id: str) -> Route:
        """Возвращает маршрут по номеру. Поиск через словарь."""
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"маршрут '{item_id}' не найден") from None

    def remove(self, item_id: str) -> None:
        """Удаляет маршрут по номеру. Отсутствующий номер - предметная ошибка."""
        if item_id not in self._items:
            raise ItemNotFoundError(f"маршрут '{item_id}' не найден")
        route = self._items.pop(item_id)
        ids = self._by_category[route.category]
        ids.discard(item_id)
        if not ids:  # пустой вид транспорта из индекса убираем
            del self._by_category[route.category]

    def find_by_category(self, category: str) -> tuple[Route, ...]:
        """Маршруты этого вида транспорта. ID берём из индекса."""
        ids = self._by_category.get(category, set())
        return tuple(self._items[item_id] for item_id in sorted(ids))

    def find_by_name(self, query: str) -> tuple[Route, ...]:
        """Маршруты, в названии которых есть query. Регистр не важен."""
        needle = query.casefold()
        found = [
            route for route in self._items.values() if needle in route.title.casefold()
        ]
        return tuple(sorted(found, key=sort_key))

    def replace_all(self, routes: list[Route]) -> None:
        """Заменяет содержимое каталога целиком.

        Сначала строим новые словари и проверяем дубликаты. Только если всё
        хорошо, подменяем старые. При ошибке каталог не меняется.
        """
        new_items: dict[str, Route] = {}
        new_index: dict[str, set[str]] = {}
        for route in routes:
            if route.item_id in new_items:
                raise DuplicateIdError(f"номер '{route.item_id}' встречается дважды")
            new_items[route.item_id] = route
            new_index.setdefault(route.category, set()).add(route.item_id)
        self._items = new_items
        self._by_category = new_index

    def __len__(self) -> int:
        """len(catalog) - число маршрутов."""
        return len(self._items)

    def __iter__(self) -> Iterator[Route]:
        """Перебор маршрутов по возрастанию номера. Генератор: yield по одному."""
        for item_id in sorted(self._items):
            yield self._items[item_id]

    def __contains__(self, item_id: object) -> bool:
        """'номер' in catalog - есть ли маршрут с таким номером."""
        return item_id in self._items


class CatalogView:
    """Только чтение (доп. задание +2): методов добавления и удаления здесь нет."""

    def __init__(self, catalog: Catalog) -> None:
        self._catalog = catalog

    def get(self, item_id: str) -> Route:
        return self._catalog.get(item_id)

    def find_by_category(self, category: str) -> tuple[Route, ...]:
        return self._catalog.find_by_category(category)

    def find_by_name(self, query: str) -> tuple[Route, ...]:
        return self._catalog.find_by_name(query)

    def __len__(self) -> int:
        return len(self._catalog)

    def __iter__(self) -> Iterator[Route]:
        return iter(self._catalog)

    def __contains__(self, item_id: object) -> bool:
        return item_id in self._catalog
