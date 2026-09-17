"""Code generation for the per-resource files plus the Alembic migration.

Each renderer returns the full file contents as a string. The output mirrors
the sample app's hand-written style: same imports, same column/method order,
same blank-line rhythm.
"""

from __future__ import annotations

from datetime import datetime

from .spec import FieldSpec, ResourceSpec, TYPE_MAP


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

def _model_field_line(f: FieldSpec) -> str:
    ann = f.py_ann if f.required else f"{f.py_ann} | None"
    if f.fk:
        # FK columns let the annotation + target column drive the type, matching
        # the sample's ``Project.owner_id`` shape.
        args = [f'ForeignKey("{f.fk_table}.{f.fk_column}", ondelete="CASCADE")', "index=True"]
        if f.required:
            args.append("nullable=False")
        return f"    {f.name}: Mapped[{ann}] = mapped_column(\n        {', '.join(args)}\n    )"
    args = [f.sa_type]
    if f.index:
        args.append("index=True")
    if f.unique:
        args.append("unique=True")
    if f.required:
        args.append("nullable=False")
    if f.has_server_default:
        args.append("server_default=true()")
    arg_str = ", ".join(args)
    line = f"    {f.name}: Mapped[{ann}] = mapped_column({arg_str})"
    if len(line) > 88:
        return f"    {f.name}: Mapped[{ann}] = mapped_column(\n        {arg_str}\n    )"
    return line


def render_model(spec: ResourceSpec) -> str:
    sa_names: set[str] = {"Uuid", "func"}
    for f in spec.fields:
        sa_names.add(TYPE_MAP[f.type][0])
    if spec.fk_fields:
        sa_names.add("ForeignKey")
    if any(f.has_server_default for f in spec.fields):
        sa_names.add("true")

    type_names = sorted(n for n in sa_names if n[0].isupper())
    func_names = sorted(n for n in sa_names if n[0].islower())
    import_names = type_names + func_names

    single_fk = len(spec.fk_fields) == 1

    lines: list[str] = []
    lines.append(f'"""{spec.class_name} resource: SQLAlchemy ORM model."""')
    lines.append("")
    lines.append("import uuid")
    lines.append("from datetime import datetime")
    lines.append("")
    lines.append(f"from sqlalchemy import {', '.join(import_names)}")
    if single_fk:
        lines.append("from sqlalchemy.orm import Mapped, mapped_column, relationship")
    else:
        lines.append("from sqlalchemy.orm import Mapped, mapped_column")
    lines.append("")
    lines.append("from app.db.base import Base")
    lines.append("")
    lines.append("")
    lines.append(f"class {spec.class_name}(Base):")
    lines.append(f'    __tablename__ = "{spec.table}"')
    lines.append("")
    lines.append(
        "    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)"
    )
    for f in spec.fields:
        lines.append(_model_field_line(f))
    lines.append("    created_at: Mapped[datetime] = mapped_column(")
    lines.append('        DateTime(timezone=True), nullable=False, server_default=func.now()')
    lines.append("    )")
    lines.append("    updated_at: Mapped[datetime] = mapped_column(")
    lines.append(
        '        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()'
    )
    lines.append("    )")
    if single_fk:
        fk = spec.fk_fields[0]
        lines.append("")
        lines.append(f'    {fk.relationship_name}: Mapped["{fk.parent_model}"] = relationship()')
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------

def _schema_field(f: FieldSpec, *, optional: bool) -> str:
    ann = f.pydantic_ann + (" | None" if optional else "")
    if f.type == "str":
        max_length = f.max_length or 255
        if optional:
            return f"    {f.name}: {ann} = Field(default=None, max_length={max_length})"
        return f"    {f.name}: {ann} = Field(min_length=1, max_length={max_length})"
    if optional:
        return f"    {f.name}: {ann} = None"
    return f"    {f.name}: {ann}"


def render_schema(spec: ResourceSpec) -> str:
    base_fields = [f for f in spec.fields if not f.fk and not f.has_server_default]
    fk_fields = spec.fk_fields
    extra_read = [f for f in spec.fields if f.fk or f.has_server_default]

    lines: list[str] = []
    lines.append(f'"""{spec.class_name} resource: Pydantic schemas (create / update / read)."""')
    lines.append("")
    lines.append("import uuid")
    lines.append("from datetime import datetime")
    lines.append("")
    if any(f.type == "str" for f in spec.fields):
        lines.append("from pydantic import Field")
        lines.append("")
    lines.append("from app.schemas.common import ORMModel")
    lines.append("")
    lines.append("")
    lines.append(f"class {spec.class_name}Base(ORMModel):")
    if base_fields:
        for f in base_fields:
            lines.append(_schema_field(f, optional=not f.required))
    else:
        lines.append("    pass")
    lines.append("")
    lines.append("")
    lines.append(f"class {spec.class_name}Create({spec.class_name}Base):")
    if fk_fields:
        for f in fk_fields:
            lines.append(f"    {f.name}: uuid.UUID")
    else:
        lines.append("    pass")
    lines.append("")
    lines.append("")
    lines.append(f"class {spec.class_name}Update(ORMModel):")
    for f in spec.fields:
        lines.append(_schema_field(f, optional=True))
    lines.append("")
    lines.append("")
    lines.append(f"class {spec.class_name}Read({spec.class_name}Base):")
    lines.append("    id: uuid.UUID")
    for f in extra_read:
        lines.append(f"    {f.name}: {f.pydantic_ann}")
    lines.append("    created_at: datetime")
    lines.append("    updated_at: datetime")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CRUD
# --------------------------------------------------------------------------

def render_crud(spec: ResourceSpec) -> str:
    lines: list[str] = []
    lines.append(f'"""{spec.class_name} resource: CRUD operations."""')
    lines.append("")
    if spec.unique_fields:
        lines.append("from sqlalchemy import select")
        lines.append("from sqlalchemy.orm import Session")
        lines.append("")
    lines.append("from app.crud.base import CRUDBase")
    lines.append(f"from app.models.{spec.name} import {spec.class_name}")
    lines.append("")
    lines.append("")
    lines.append(f"class {spec.crud_class}(CRUDBase[{spec.class_name}]):")
    if spec.unique_fields:
        for i, f in enumerate(spec.unique_fields):
            if i > 0:
                lines.append("")
            lines.append(
                f"    def get_by_{f.name}(self, db: Session, *, {f.name}: {f.py_ann})"
                f" -> {spec.class_name} | None:"
            )
            lines.append(
                f"        stmt = select({spec.class_name}).where("
                f"{spec.class_name}.{f.name} == {f.name})"
            )
            lines.append("        return db.scalars(stmt).first()")
    else:
        lines.append("    pass")
    lines.append("")
    lines.append("")
    lines.append(f"{spec.crud_instance} = {spec.crud_class}({spec.class_name})")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Route
# --------------------------------------------------------------------------

def _fk_create_check(resource: str, f: FieldSpec) -> str:
    return (
        f"    if not crud.{f.parent_resource}.get(db, id={resource}_in.{f.name}):\n"
        f"        raise HTTPException(\n"
        f'            status_code=status.HTTP_404_NOT_FOUND, detail="{f.parent_model} not found."\n'
        f"        )"
    )


def _fk_update_check(resource: str, f: FieldSpec) -> str:
    return (
        f"    if {resource}_in.{f.name} is not None and not "
        f"crud.{f.parent_resource}.get(db, id={resource}_in.{f.name}):\n"
        f"        raise HTTPException(\n"
        f'            status_code=status.HTTP_404_NOT_FOUND, detail="{f.parent_model} not found."\n'
        f"        )"
    )


def render_route(spec: ResourceSpec) -> str:
    resource = spec.name
    table = spec.table
    class_name = spec.class_name

    lines: list[str] = []
    lines.append(f'"""{class_name} resource: HTTP endpoints."""')
    lines.append("")
    lines.append("import uuid")
    lines.append("")
    lines.append("from fastapi import APIRouter, HTTPException, status")
    lines.append("")
    lines.append("from app import crud")
    lines.append("from app.api.deps import DBSession")
    lines.append(
        f"from app.schemas.{resource} import {class_name}Create, {class_name}Read, {class_name}Update"
    )
    lines.append("")
    lines.append("router = APIRouter()")
    lines.append("")
    lines.append("")

    # create
    lines.append(
        f'@router.post("", response_model={class_name}Read, status_code=status.HTTP_201_CREATED)'
    )
    lines.append(
        f"def create_{resource}(*, db: DBSession, {resource}_in: {class_name}Create) -> {class_name}Read:"
    )
    for f in spec.unique_fields:
        lines.append(
            f"    existing = crud.{resource}.get_by_{f.name}(db, {f.name}={resource}_in.{f.name})"
        )
        lines.append("    if existing:")
        lines.append("        raise HTTPException(")
        lines.append(
            f'            status_code=status.HTTP_409_CONFLICT, '
            f'detail="A {resource} with this {f.name} already exists."'
        )
        lines.append("        )")
    for f in spec.fk_fields:
        lines.append(_fk_create_check(resource, f))
    lines.append(f"    return crud.{resource}.create(db, obj_in={resource}_in.model_dump())")
    lines.append("")
    lines.append("")

    # list
    lines.append(f'@router.get("", response_model=list[{class_name}Read])')
    lines.append(
        f"def list_{table}(*, db: DBSession, skip: int = 0, limit: int = 100) -> list[{class_name}Read]:"
    )
    lines.append(f"    return crud.{resource}.list(db, skip=skip, limit=limit)")
    lines.append("")
    lines.append("")

    # get
    lines.append(f'@router.get("/{{{resource}_id}}", response_model={class_name}Read)')
    lines.append(
        f"def get_{resource}(*, db: DBSession, {resource}_id: uuid.UUID) -> {class_name}Read:"
    )
    lines.append(f"    {resource} = crud.{resource}.get(db, id={resource}_id)")
    lines.append(f"    if not {resource}:")
    lines.append(
        f'        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, '
        f'detail="{class_name} not found.")'
    )
    lines.append(f"    return {resource}")
    lines.append("")
    lines.append("")

    # update
    lines.append(f'@router.patch("/{{{resource}_id}}", response_model={class_name}Read)')
    lines.append(
        f"def update_{resource}(*, db: DBSession, {resource}_id: uuid.UUID, "
        f"{resource}_in: {class_name}Update) -> {class_name}Read:"
    )
    lines.append(f"    {resource} = crud.{resource}.get(db, id={resource}_id)")
    lines.append(f"    if not {resource}:")
    lines.append(
        f'        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, '
        f'detail="{class_name} not found.")'
    )
    for f in spec.fk_fields:
        lines.append(_fk_update_check(resource, f))
    lines.append(
        f"    return crud.{resource}.update(db, db_obj={resource}, "
        f"obj_in={resource}_in.model_dump(exclude_unset=True))"
    )
    lines.append("")
    lines.append("")

    # delete
    lines.append(f'@router.delete("/{{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)')
    lines.append(
        f"def delete_{resource}(*, db: DBSession, {resource}_id: uuid.UUID) -> None:"
    )
    lines.append(f"    {resource} = crud.{resource}.get(db, id={resource}_id)")
    lines.append(f"    if not {resource}:")
    lines.append(
        f'        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, '
        f'detail="{class_name} not found.")'
    )
    lines.append(f"    crud.{resource}.delete(db, db_obj={resource})")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Migration
# --------------------------------------------------------------------------

def render_migration(
    spec: ResourceSpec, revision: str, down_revision: str | None, create_date: str | None = None
) -> str:
    date = create_date or datetime.utcnow().strftime("%Y-%m-%d")
    down = f'"{down_revision}"' if down_revision else "None"

    lines: list[str] = []
    lines.append(f'"""{spec.table} table')
    lines.append("")
    lines.append(f"Revision ID: {revision}")
    lines.append(f"Revises: {down_revision or ''}")
    lines.append(f"Create Date: {date}")
    lines.append("")
    lines.append('"""')
    lines.append("from alembic import op")
    lines.append("import sqlalchemy as sa")
    lines.append("")
    lines.append("# revision identifiers, used by Alembic.")
    lines.append(f'revision = "{revision}"')
    lines.append(f"down_revision = {down}")
    lines.append("branch_labels = None")
    lines.append("depends_on = None")
    lines.append("")
    lines.append("")
    lines.append("def upgrade() -> None:")
    lines.append("    op.create_table(")
    lines.append(f'        "{spec.table}",')
    lines.append('        sa.Column("id", sa.Uuid(), nullable=False),')
    for f in spec.fields:
        parts = [f'sa.Column("{f.name}", {f.sa_migration_type}']
        if f.has_server_default:
            parts.append('server_default=sa.text("true")')
        parts.append(f"nullable={'False' if f.required else 'True'}")
        lines.append(f"        {', '.join(parts)}),")
    for col in ("created_at", "updated_at"):
        lines.append(
            f'        sa.Column("{col}", sa.DateTime(timezone=True), '
            f'server_default=sa.text("now()"), nullable=False),'
        )
    for f in spec.unique_fields:
        lines.append(f'        sa.UniqueConstraint("{f.name}"),')
    for f in spec.fk_fields:
        lines.append(
            f'        sa.ForeignKeyConstraint(["{f.name}"], '
            f'["{f.fk_table}.{f.fk_column}"], ondelete="CASCADE"),'
        )
    lines.append('        sa.PrimaryKeyConstraint("id"),')
    lines.append("    )")
    for f in spec.indexed_fields:
        lines.append(
            f'    op.create_index(op.f("ix_{spec.table}_{f.name}"), '
            f'"{spec.table}", ["{f.name}"], unique=False)'
        )
    lines.append("")
    lines.append("")
    lines.append("def downgrade() -> None:")
    for f in spec.indexed_fields:
        lines.append(
            f'    op.drop_index(op.f("ix_{spec.table}_{f.name}"), table_name="{spec.table}")'
        )
    lines.append(f'    op.drop_table("{spec.table}")')
    lines.append("")
    return "\n".join(lines)
