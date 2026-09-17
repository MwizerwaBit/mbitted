"""Command-line entry point.

Reads a resource spec and emits the matching files into a FastAPI app that
follows the sample-app conventions. Run::

    python -m scaffolder widget.json --app-root ../sample-app
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import wire
from .render import render_crud, render_migration, render_model, render_route, render_schema
from .spec import load_spec


def find_head_revision(versions_dir: Path) -> tuple[str | None, str]:
    """Return ``(head_revision, next_revision)`` by scanning the versions dir."""
    revs: dict[str, str] = {}
    for f in versions_dir.glob("*.py"):
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^revision\s*=\s*["\']([^"\']+)["\']', text, re.M)
        if not m:
            continue
        d = re.search(r"^down_revision\s*=\s*(.+)$", text, re.M)
        revs[m.group(1)] = d.group(1).strip() if d else "None"

    referenced: set[str] = set()
    for down in revs.values():
        referenced.update(re.findall(r'["\']([^"\']+)["\']', down))
    heads = [r for r in revs if r not in referenced]
    head = heads[0] if heads else None
    next_num = max((int(r) for r in revs if r.isdigit()), default=0) + 1
    return head, f"{next_num:04d}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scaffolder",
        description="Generate a FastAPI resource (model, schemas, CRUD, route, migration).",
    )
    parser.add_argument("spec", help="path to a resource spec JSON file")
    parser.add_argument(
        "--app-root",
        help="FastAPI app root (defaults to ../sample-app relative to this package)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print generated files to stdout instead of writing them",
    )
    args = parser.parse_args(argv)

    default_root = Path(__file__).resolve().parent.parent / "sample-app"
    app_root = Path(args.app_root) if args.app_root else default_root
    if not (app_root / "app").is_dir() or not (app_root / "alembic").is_dir():
        print(
            f"error: {app_root} does not look like a FastAPI app (missing app/ or alembic/)",
            file=sys.stderr,
        )
        return 2

    try:
        spec = load_spec(args.spec)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    versions_dir = app_root / "alembic" / "versions"
    head, next_rev = find_head_revision(versions_dir)

    new_files: dict[Path, str] = {
        app_root / "app" / "models" / f"{spec.name}.py": render_model(spec),
        app_root / "app" / "schemas" / f"{spec.name}.py": render_schema(spec),
        app_root / "app" / "crud" / f"{spec.name}.py": render_crud(spec),
        app_root / "app" / "api" / "routes" / f"{spec.name}.py": render_route(spec),
    }
    # Emit a migration only when this table has none yet (idempotent re-runs).
    if list(versions_dir.glob(f"*_create_{spec.table}.py")):
        print(f"skip  migration for '{spec.table}' (already exists)")
    else:
        new_files[versions_dir / f"{next_rev}_create_{spec.table}.py"] = render_migration(
            spec, next_rev, head
        )

    wiring_files: dict[Path, callable] = {
        app_root / "app" / "models" / "__init__.py": wire.patch_models_init,
        app_root / "app" / "schemas" / "__init__.py": wire.patch_schemas_init,
        app_root / "app" / "crud" / "__init__.py": wire.patch_crud_init,
        app_root / "app" / "api" / "routes" / "__init__.py": wire.patch_routes_init,
        app_root / "app" / "main.py": wire.patch_main,
    }

    if args.dry_run:
        for path, content in new_files.items():
            print(f"# ---- {path.name} ----")
            print(content)
        for path, patcher in wiring_files.items():
            if path.is_file():
                print(f"# ---- {path.name} (patched) ----")
                print(patcher(path.read_text(encoding="utf-8"), spec))
        return 0

    for path, content in new_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(app_root)}")

    for path, patcher in wiring_files.items():
        if not path.is_file():
            print(f"skip  {path.relative_to(app_root)} (not found)")
            continue
        patched = patcher(path.read_text(encoding="utf-8"), spec)
        path.write_text(patched, encoding="utf-8")
        print(f"wired {path.relative_to(app_root)}")

    print(
        f"\nScaffolded {spec.class_name} ({spec.table}) with {len(spec.fields)} fields "
        f"-> {spec.table} routes at {spec.table!r}."
    )
    return 0
