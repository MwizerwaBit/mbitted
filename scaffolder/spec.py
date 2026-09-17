"""Resource spec model, validation, and naming helpers.

A spec is a small JSON document describing one resource::

    {
      "name": "widget",
      "fields": [
        {"name": "name", "type": "str", "required": true, "max_length": 255, "unique": true},
        {"name": "owner_id", "type": "uuid", "required": true, "fk": "users.id", "index": true}
      ]
    }

``name`` is the singular snake_case resource name; the table name defaults to
its plural (override with ``"table"``). Field ``type`` is one of ``str``,
``text``, ``int``, ``float``, ``bool``, ``datetime``, or ``uuid``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Field names the scaffolder always emits itself.
RESERVED_FIELDS = {"id", "created_at", "updated_at"}

# spec type -> (SQLAlchemy column type name, Mapped[...] annotation, Pydantic annotation)
TYPE_MAP: dict[str, tuple[str, str, str]] = {
    "str": ("String", "str", "str"),
    "text": ("Text", "str", "str"),
    "int": ("Integer", "int", "int"),
    "float": ("Float", "float", "float"),
    "bool": ("Boolean", "bool", "bool"),
    "datetime": ("DateTime", "datetime", "datetime"),
    "uuid": ("Uuid", "uuid.UUID", "uuid.UUID"),
}


def to_snake(name: str) -> str:
    """``WidgetType`` / ``widget-type`` / ``widgetType`` -> ``widget_type``."""
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    return name.strip("_").lower()


def to_pascal(name: str) -> str:
    """``widget_type`` -> ``WidgetType``."""
    return "".join(part.capitalize() for part in re.split(r"[_\-\s]+", name) if part)


def pluralize(word: str) -> str:
    """Naive English pluralization (``user`` -> ``users``, ``category`` -> ``categories``)."""
    if re.search(r"(s|x|z|ch|sh)$", word):
        return word + "es"
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    return word + "s"


def singularize(word: str) -> str:
    """Best-effort inverse of :func:`pluralize` (``users`` -> ``user``)."""
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("es") and re.search(r"(s|x|z|ch|sh)$", word[:-2]):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


@dataclass
class FieldSpec:
    name: str
    type: str
    required: bool = False
    max_length: int | None = None
    unique: bool = False
    fk: str | None = None
    index: bool = False

    @property
    def py_ann(self) -> str:
        """SQLAlchemy ``Mapped[...]`` annotation."""
        return TYPE_MAP[self.type][1]

    @property
    def pydantic_ann(self) -> str:
        """Pydantic annotation."""
        return TYPE_MAP[self.type][2]

    @property
    def sa_type(self) -> str:
        """SQLAlchemy column type expression."""
        if self.type == "str":
            return f"String({self.max_length or 255})"
        if self.type == "datetime":
            return "DateTime(timezone=True)"
        return TYPE_MAP[self.type][0]

    @property
    def sa_migration_type(self) -> str:
        """Alembic ``sa.<Type>(...)`` expression."""
        if self.type == "str":
            return f"sa.String(length={self.max_length or 255})"
        if self.type == "text":
            return "sa.Text()"
        if self.type == "int":
            return "sa.Integer()"
        if self.type == "float":
            return "sa.Float()"
        if self.type == "bool":
            return "sa.Boolean()"
        if self.type == "datetime":
            return "sa.DateTime(timezone=True)"
        return "sa.Uuid()"

    @property
    def has_server_default(self) -> bool:
        """True when the column gets a SQL server default (required bool)."""
        return self.type == "bool" and self.required

    @property
    def fk_table(self) -> str | None:
        if not self.fk:
            return None
        return self.fk.split(".")[0]

    @property
    def fk_column(self) -> str:
        if not self.fk:
            return "id"
        parts = self.fk.split(".")
        return parts[1] if len(parts) > 1 else "id"

    @property
    def relationship_name(self) -> str:
        if self.name.endswith("_id"):
            return self.name[:-3]
        return self.name

    @property
    def parent_resource(self) -> str:
        """Singular snake_case of the FK target table (``users`` -> ``user``)."""
        return singularize(self.fk_table or "")

    @property
    def parent_model(self) -> str:
        return to_pascal(self.parent_resource)


@dataclass
class ResourceSpec:
    name: str
    table: str
    class_name: str
    fields: list[FieldSpec]

    @property
    def fk_fields(self) -> list[FieldSpec]:
        return [f for f in self.fields if f.fk]

    @property
    def unique_fields(self) -> list[FieldSpec]:
        return [f for f in self.fields if f.unique]

    @property
    def indexed_fields(self) -> list[FieldSpec]:
        return [f for f in self.fields if f.index or f.fk]

    @property
    def crud_class(self) -> str:
        return f"CRUD{self.class_name}"

    @property
    def crud_instance(self) -> str:
        return self.name


def parse_field(raw: dict[str, Any]) -> FieldSpec:
    name = to_snake(str(raw.get("name", "")))
    type_ = str(raw.get("type", "str"))
    if not name:
        raise ValueError("field is missing a name")
    if name in RESERVED_FIELDS:
        raise ValueError(
            f"field {name!r} is reserved (id/created_at/updated_at are auto-generated)"
        )
    if type_ not in TYPE_MAP:
        raise ValueError(
            f"field {name!r}: unknown type {type_!r} (expected one of {sorted(TYPE_MAP)})"
        )
    return FieldSpec(
        name=name,
        type=type_,
        required=bool(raw.get("required", False)),
        max_length=raw.get("max_length"),
        unique=bool(raw.get("unique", False)),
        fk=raw.get("fk"),
        index=bool(raw.get("index", False)),
    )


def parse_spec(raw: dict[str, Any]) -> ResourceSpec:
    if not isinstance(raw, dict):
        raise ValueError("spec must be a JSON object")
    name = to_snake(str(raw.get("name", "")))
    if not name:
        raise ValueError("spec is missing a resource 'name'")
    table = to_snake(str(raw.get("table") or pluralize(name)))
    fields = [parse_field(f) for f in raw.get("fields", [])]
    seen: set[str] = set()
    for f in fields:
        if f.name in seen:
            raise ValueError(f"duplicate field {f.name!r}")
        seen.add(f.name)
    return ResourceSpec(name=name, table=table, class_name=to_pascal(name), fields=fields)


def load_spec(path: str) -> ResourceSpec:
    import json

    with open(path, encoding="utf-8") as fh:
        return parse_spec(json.load(fh))
