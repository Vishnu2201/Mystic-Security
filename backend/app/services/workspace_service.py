from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def get_workspace(db: Session, workspace_id: UUID) -> Optional[Workspace]:
    """Retrieve a single workspace by its primary key UUID."""
    return db.get(Workspace, workspace_id)


def get_workspace_by_name(db: Session, name: str) -> Optional[Workspace]:
    """Retrieve a single workspace by its unique name."""
    stmt = select(Workspace).where(Workspace.name == name)
    return db.scalar(stmt)


def list_workspaces(db: Session, skip: int = 0, limit: int = 100) -> List[Workspace]:
    """List workspaces with pagination support."""
    stmt = select(Workspace).order_by(Workspace.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_workspace(db: Session, schema: WorkspaceCreate) -> Workspace:
    """Create a new Workspace entity."""
    existing = get_workspace_by_name(db, schema.name)
    if existing:
        raise ValueError(f"Workspace with name '{schema.name}' already exists.")

    db_workspace = Workspace(
        name=schema.name,
        description=schema.description,
    )
    try:
        db.add(db_workspace)
        db.commit()
        db.refresh(db_workspace)
        return db_workspace
    except IntegrityError as err:
        db.rollback()
        raise ValueError(f"Workspace with name '{schema.name}' already exists.") from err


def update_workspace(db: Session, db_workspace: Workspace, schema: WorkspaceUpdate) -> Workspace:
    """
    Update an existing Workspace entity using partial model data.
    Uses schema.model_fields_set to accurately distinguish between:
    - Omitted fields (not in model_fields_set) -> leave existing value unchanged
    - Explicitly provided nulls ('description': null in JSON) -> set database column to NULL
    - Explicitly provided values ('description': 'text' in JSON) -> set database column to 'text'
    """
    if "name" in schema.model_fields_set:
        if schema.name is None:
            raise ValueError("Workspace name cannot be null.")
        if schema.name != db_workspace.name:
            existing = get_workspace_by_name(db, schema.name)
            if existing:
                raise ValueError(f"Workspace with name '{schema.name}' already exists.")
            db_workspace.name = schema.name

    if "description" in schema.model_fields_set:
        db_workspace.description = schema.description

    try:
        db.commit()
        db.refresh(db_workspace)
        return db_workspace
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Workspace update failed due to database constraint violation.") from err


def delete_workspace(db: Session, db_workspace: Workspace) -> None:
    """Delete an existing Workspace entity."""
    try:
        db.delete(db_workspace)
        db.commit()
    except Exception:
        db.rollback()
        raise
