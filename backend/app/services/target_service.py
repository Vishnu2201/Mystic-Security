from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.target import Target
from app.schemas.target import TargetCreate, TargetUpdate
from app.services.workspace_service import get_workspace


def get_target(db: Session, target_id: UUID) -> Optional[Target]:
    """Retrieve a single target by its primary key UUID."""
    return db.get(Target, target_id)


def get_target_by_identifier(db: Session, workspace_id: UUID, identifier: str) -> Optional[Target]:
    """Retrieve a target by unique workspace ID and identifier combination."""
    stmt = select(Target).where(
        Target.workspace_id == workspace_id,
        Target.identifier == identifier,
    )
    return db.scalar(stmt)


def list_targets(
    db: Session,
    workspace_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Target]:
    """List targets with optional workspace_id filtering and pagination support."""
    stmt = select(Target)
    if workspace_id is not None:
        stmt = stmt.where(Target.workspace_id == workspace_id)
    stmt = stmt.order_by(Target.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_target(db: Session, schema: TargetCreate) -> Target:
    """Create a new Target entity within an existing Workspace."""
    workspace = get_workspace(db, schema.workspace_id)
    if not workspace:
        raise ValueError(f"Workspace with ID '{schema.workspace_id}' does not exist.")

    existing = get_target_by_identifier(db, schema.workspace_id, schema.identifier)
    if existing:
        raise ValueError(
            f"Target with identifier '{schema.identifier}' already exists in workspace '{schema.workspace_id}'."
        )

    db_target = Target(
        workspace_id=schema.workspace_id,
        name=schema.name,
        target_category=schema.target_category,
        identifier=schema.identifier,
        description=schema.description,
        ip_address=schema.ip_address,
        network_range=schema.network_range,
    )
    try:
        db.add(db_target)
        db.commit()
        db.refresh(db_target)
        return db_target
    except IntegrityError as err:
        db.rollback()
        raise ValueError(
            f"Target with identifier '{schema.identifier}' already exists in workspace '{schema.workspace_id}'."
        ) from err


def update_target(db: Session, db_target: Target, schema: TargetUpdate) -> Target:
    """
    Update an existing Target entity using partial model data.
    Evaluates final effective (workspace_id, identifier) state before mutation
    to ensure strict uniqueness collision detection across all 4 field change combinations.
    """
    # 1. Evaluate effective workspace_id
    effective_workspace_id = db_target.workspace_id
    if "workspace_id" in schema.model_fields_set:
        if schema.workspace_id is None:
            raise ValueError("Target workspace_id cannot be null.")
        if schema.workspace_id != db_target.workspace_id:
            workspace = get_workspace(db, schema.workspace_id)
            if not workspace:
                raise ValueError(f"Workspace with ID '{schema.workspace_id}' does not exist.")
            effective_workspace_id = schema.workspace_id

    # 2. Evaluate effective identifier
    effective_identifier = db_target.identifier
    if "identifier" in schema.model_fields_set:
        if schema.identifier is None:
            raise ValueError("Target identifier cannot be null.")
        effective_identifier = schema.identifier

    # 3. Check uniqueness collision for effective (workspace_id, identifier) combination
    if effective_workspace_id != db_target.workspace_id or effective_identifier != db_target.identifier:
        existing = get_target_by_identifier(db, effective_workspace_id, effective_identifier)
        if existing and existing.id != db_target.id:
            raise ValueError(
                f"Target with identifier '{effective_identifier}' already exists in workspace '{effective_workspace_id}'."
            )

    # 4. Apply mutations to db_target
    if "workspace_id" in schema.model_fields_set:
        db_target.workspace_id = effective_workspace_id

    if "name" in schema.model_fields_set:
        if schema.name is None:
            raise ValueError("Target name cannot be null.")
        db_target.name = schema.name

    if "target_category" in schema.model_fields_set:
        if schema.target_category is None:
            raise ValueError("Target target_category cannot be null.")
        db_target.target_category = schema.target_category

    if "identifier" in schema.model_fields_set:
        db_target.identifier = effective_identifier

    if "description" in schema.model_fields_set:
        db_target.description = schema.description

    if "ip_address" in schema.model_fields_set:
        db_target.ip_address = schema.ip_address

    if "network_range" in schema.model_fields_set:
        db_target.network_range = schema.network_range

    try:
        db.commit()
        db.refresh(db_target)
        return db_target
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Target update failed due to database constraint violation.") from err


def delete_target(db: Session, db_target: Target) -> None:
    """Delete an existing Target entity."""
    try:
        db.delete(db_target)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Cannot delete target because it is referenced by existing assessment records.") from err
    except Exception:
        db.rollback()
        raise
