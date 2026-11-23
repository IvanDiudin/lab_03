"""Исключения каталога. Все ошибки наследуются от CatalogError."""


class CatalogError(Exception):
    """Базовая ошибка каталога."""


class InvalidItemError(CatalogError):
    """Неверная сущность: поле не прошло проверку при создании."""


class DuplicateIdError(CatalogError):
    """В каталоге уже есть объект с таким идентификатором."""


class ItemNotFoundError(CatalogError):
    """Объект с указанным идентификатором не найден."""


class UnsupportedVersionError(CatalogError):
    """Версия формата файла не поддерживается."""


class CorruptedFileError(CatalogError):
    """Файл повреждён: JSON не читается или структура не совпадает с форматом."""
