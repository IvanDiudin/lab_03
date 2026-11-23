"""Сохранение каталога в JSON и загрузка из JSON."""

import json
from typing import Any

from catalog.catalog import Catalog
from catalog.constants import FORMAT_VERSION, SUPPORTED_VERSIONS
from catalog.errors import (
    CorruptedFileError,
    DuplicateIdError,
    InvalidItemError,
    UnsupportedVersionError,
)
from catalog.route import Route


def save_catalog(catalog: Catalog, path: str) -> None:
    """Записывает каталог в JSON-файл."""
    document = {
        "format_version": FORMAT_VERSION,
        "items": [route.to_dict() for route in catalog],
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(document, file, ensure_ascii=False, indent=2)
        file.write("\n")


def migrate_v1_item(raw: dict[str, Any]) -> dict[str, Any]:
    """Версия 1: год строкой в поле date. Версия 2: число в поле year."""
    migrated = dict(raw)
    if "date" in migrated:
        migrated["year"] = int(migrated.pop("date"))
    return migrated


def _migrate_items(items: list[Any], path: str) -> list[Any]:
    """Мигрирует элементы версии 1."""
    result: list[Any] = []
    for number, raw in enumerate(items, start=1):
        if not isinstance(raw, dict):
            raise CorruptedFileError(f"{path}: элемент {number} не является объектом")
        try:
            result.append(migrate_v1_item(raw))
        except ValueError as error:
            raise CorruptedFileError(
                f"{path}: в элементе {number} год не число"
            ) from error
    return result


def parse_document(document: Any, path: str) -> list[Route]:
    """Проверяет структуру документа и возвращает список маршрутов."""
    if not isinstance(document, dict):
        raise CorruptedFileError(f"{path}: корень документа должен быть объектом")
    if "format_version" not in document:
        raise CorruptedFileError(f"{path}: нет поля format_version")
    version = document["format_version"]
    if version not in SUPPORTED_VERSIONS:
        raise UnsupportedVersionError(f"{path}: версия {version} не поддерживается")
    items = document.get("items")
    if not isinstance(items, list):
        raise CorruptedFileError(f"{path}: поле items должно быть списком")
    if version == 1:
        items = _migrate_items(items, path)

    routes: list[Route] = []
    for number, raw in enumerate(items, start=1):
        if not isinstance(raw, dict):
            raise CorruptedFileError(f"{path}: элемент {number} не является объектом")
        try:
            routes.append(Route.from_dict(raw))
        except KeyError as error:
            raise CorruptedFileError(
                f"{path}: в элементе {number} нет поля {error}"
            ) from error
        except InvalidItemError as error:
            raise CorruptedFileError(
                f"{path}: элемент {number} неверный: {error}"
            ) from error
    return routes


def load_catalog(catalog: Catalog, path: str) -> None:
    """Загружает маршруты из JSON в существующий каталог (атомарно)."""
    try:
        with open(path, encoding="utf-8") as file:
            document = json.load(file)
    except json.JSONDecodeError as error:
        raise CorruptedFileError(f"{path}: JSON не читается: {error.msg}") from error

    routes = parse_document(document, path)
    try:
        catalog.replace_all(routes)
    except DuplicateIdError as error:
        raise CorruptedFileError(f"{path}: {error}") from error
