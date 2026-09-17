"""Wiring edits: register a new resource in the app's ``__init__`` modules and
``main.py`` so the generated files are actually imported and routed.

Every patch is idempotent — running the scaffolder twice for the same resource
does not duplicate imports or ``__all__`` entries.
"""

from __future__ import annotations

import re

from .spec import ResourceSpec


def _extend_all(text: str, names: list[str]) -> str:
    """Add *names* to the ``__all__`` list in *text* (idempotent)."""
    m = re.search(r"__all__\s*=\s*\[(.*?)\]", text, re.DOTALL)
    if not m:
        return text
    body = m.group(1)
    existing = set(re.findall(r'["\']([^"\']+)["\']', body))
    to_add = [n for n in names if n not in existing]
    if not to_add:
        return text
    if "\n" in body:
        indent = "    "
        addition = "".join(f'{indent}"{n}",\n' for n in to_add)
        new_body = body + addition
    else:
        addition = "".join(f', "{n}"' for n in to_add)
        new_body = body + addition
    return text[: m.start(1)] + new_body + text[m.end(1):]


def _insert_after_imports(text: str, line: str) -> str:
    """Insert an import *line* after the last import in *text*."""
    if line in text:
        return text
    lines = text.split("\n")
    last_import = -1
    for i, ln in enumerate(lines):
        if ln.startswith(("from ", "import ")):
            last_import = i
    if last_import == -1:
        return text.rstrip("\n") + "\n" + line + "\n"
    lines.insert(last_import + 1, line)
    return "\n".join(lines)


def _append_to_import(text: str, module: str) -> str:
    """Append *module* to a ``from ... import a, b`` line (idempotent)."""
    m = re.search(r"^(from app\.api\.routes import .+)$", text, re.M)
    if not m:
        return text
    line = m.group(1)
    modules = [x.strip() for x in line.split("import", 1)[1].split(",") if x.strip()]
    if module in modules:
        return text
    return text.replace(line, line + f", {module}")


def patch_models_init(text: str, spec: ResourceSpec) -> str:
    line = f"from app.models.{spec.name} import {spec.class_name}"
    return _extend_all(_insert_after_imports(text, line), [spec.class_name])


def patch_schemas_init(text: str, spec: ResourceSpec) -> str:
    line = (
        f"from app.schemas.{spec.name} import "
        f"{spec.class_name}Create, {spec.class_name}Read, {spec.class_name}Update"
    )
    names = [f"{spec.class_name}Create", f"{spec.class_name}Read", f"{spec.class_name}Update"]
    return _extend_all(_insert_after_imports(text, line), names)


def patch_crud_init(text: str, spec: ResourceSpec) -> str:
    line = f"from app.crud.{spec.name} import {spec.crud_instance}"
    return _extend_all(_insert_after_imports(text, line), [spec.crud_instance])


def patch_routes_init(text: str, spec: ResourceSpec) -> str:
    return _extend_all(_append_to_import(text, spec.name), [spec.name])


def patch_main(text: str, spec: ResourceSpec) -> str:
    text = _append_to_import(text, spec.name)
    include = (
        f'app.include_router({spec.name}.router, '
        f'prefix=f"{{settings.api_v1_prefix}}/{spec.table}", tags=["{spec.table}"])'
    )
    if include in text:
        return text
    last = text.rfind("app.include_router")
    if last == -1:
        return text
    close = text.index(")", last)
    eol = text.index("\n", close)
    insert_at = eol + 1
    return text[:insert_at] + f"{include}\n" + text[insert_at:]
