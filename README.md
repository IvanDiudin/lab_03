# Лабораторная работа 3. Каталог транспортных маршрутов

Пакет `catalog` описывает предметную модель (транспортный маршрут) и каталог
с поиском и JSON-хранением.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -e ".[dev]"
```

## Проверка

```bash
python -m pytest
ruff check .
mypy src
```

## Модель

`Route` (dataclass, frozen) содержит поля:

| поле | тип | ограничение |
|---|---|---|
| `item_id` | str | уникальный номер маршрута, непустой |
| `title` | str | название, непустое (например, «Вокзал - Парк») |
| `category` | str | вид транспорта, непустой (автобус, трамвай, троллейбус, метро) |
| `year` | int | год открытия, от 1850 до 2100 |
| `stops` | int | число остановок, не меньше двух (поле варианта) |
| `duration_min` | int | время в пути в минутах, больше нуля (поле варианта) |

Инварианты проверяются при создании (`__post_init__`). Неверный маршрут
в каталог не попадает.

## Каталог

- `add(route)`, `get(item_id)`, `remove(item_id)`;
- `find_by_category(category)`, `find_by_name(query)` — возвращают кортеж;
- `len()`, итерация, `in`.

Хранение: словарь `item_id -> Route`, поэтому `get` не перебирает все маршруты.
Порядок итерации: по возрастанию `item_id`.

## Хранение в JSON

```python
from catalog.catalog import Catalog
from catalog.storage import load_catalog, save_catalog

save_catalog(catalog, "routes.json")
load_catalog(catalog, "routes.json")
```

Документ содержит поле `format_version` (сейчас 2). Версия 1 читается
через миграцию (поле `date` становится `year`). Другие версии отклоняются.

Загрузка атомарна: если файл повреждён, существующий каталог не меняется.

## Исключения

Все ошибки наследуются от `CatalogError`:
- `InvalidItemError` — неверный маршрут;
- `DuplicateIdError` — дубликат номера;
- `ItemNotFoundError` — маршрут не найден;
- `UnsupportedVersionError` — неподдерживаемая версия;
- `CorruptedFileError` — повреждённый файл.

## Дополнительные задания

- **Неуникальный индекс по виду транспорта** (`catalog.py`, `_by_category`).
  Поддерживается при добавлении, удалении, замене и загрузке.
- **Read-only view** (`CatalogView`): только чтение, без `add` и `remove`.
- **Миграция версии 1 в версию 2** (`storage.py`, `migrate_v1_item`).
