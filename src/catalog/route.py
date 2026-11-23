"""Сущность Route: транспортный маршрут с проверкой инвариантов при создании."""

from dataclasses import dataclass
from typing import Any

from catalog.constants import MAX_YEAR, MIN_STOPS, MIN_YEAR
from catalog.errors import InvalidItemError


def check_text(name: str, value: object) -> None:
    """Поле должно быть непустой строкой (пробелы по краям не считаются)."""
    if not isinstance(value, str) or value.strip() == "":
        raise InvalidItemError(f"поле '{name}' должно быть непустой строкой")


def check_int(name: str, value: object) -> None:
    """Поле должно быть целым числом. bool тоже не подходит, хотя это int."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise InvalidItemError(f"поле '{name}' должно быть целым числом")


@dataclass(frozen=True)
class Route:
    """Маршрут. frozen=True: после создания поля нельзя изменить."""

    item_id: str
    title: str
    category: str
    year: int
    stops: int
    duration_min: int

    def __post_init__(self) -> None:
        """Проверяет все инварианты. Неверный маршрут не создаётся."""
        check_text("item_id", self.item_id)
        check_text("title", self.title)
        check_text("category", self.category)
        check_int("year", self.year)
        if not MIN_YEAR <= self.year <= MAX_YEAR:
            raise InvalidItemError(
                f"год должен быть от {MIN_YEAR} до {MAX_YEAR}, а не {self.year}"
            )
        check_int("stops", self.stops)
        if self.stops < MIN_STOPS:
            raise InvalidItemError(
                f"у маршрута должно быть не меньше {MIN_STOPS} остановок"
            )
        check_int("duration_min", self.duration_min)
        if self.duration_min <= 0:
            raise InvalidItemError("время в пути должно быть больше нуля")

    def to_dict(self) -> dict[str, Any]:
        """Превращает маршрут в словарь для записи в JSON."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "category": self.category,
            "year": self.year,
            "stops": self.stops,
            "duration_min": self.duration_min,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Route":
        """Создаёт маршрут из словаря."""
        return cls(
            item_id=data["item_id"],
            title=data["title"],
            category=data["category"],
            year=data["year"],
            stops=data["stops"],
            duration_min=data["duration_min"],
        )
