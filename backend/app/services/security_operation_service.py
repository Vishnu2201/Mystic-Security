from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.enums import (
    SecurityOperationStatus,
    SecurityOperationType,
)
from app.models.security_operation import SecurityOperation
from app.schemas.security_operation import SecurityOperationCreate
from app.services.workspace_service import get_workspace
from app.services.target_service import get_target
from app.services.authorization_service import authorize_security_operation
from app.core.authorization import classify_operation_activity
from app.security_operations.registry import get_executor


def get_security_operation(db: Session, operation_id: UUID) -> Optional[SecurityOperation]:
    """Retrieve a single SecurityOperation by its primary key UUID."""
    return db.get(SecurityOperation, operation_id)


def list_security_operations(
    db: Session,
    workspace_id: Optional[UUID] = None,
    target_id: Optional[UUID] = None,
    operation_type: Optional[SecurityOperationType] = None,
    status_filter: Optional[SecurityOperationStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[SecurityOperation]:
    """List security operations with optional filtering and pagination support."""
    stmt = select(SecurityOperation)
    if workspace_id is not None:
        stmt = stmt.where(SecurityOperation.workspace_id == workspace_id)
    if target_id is not None:
        stmt = stmt.where(SecurityOperation.target_id == target_id)
    if operation_type is not None:
        stmt = stmt.where(SecurityOperation.operation_type == operation_type)
    if status_filter is not None:
        stmt = stmt.where(SecurityOperation.status == status_filter)

    stmt = stmt.order_by(SecurityOperation.requested_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_and_execute_security_operation(
    db: Session,
    schema: SecurityOperationCreate,
) -> Tuple[SecurityOperation, int]:
    """
    Central Security Operation Execution Service (Phase 0.9).
    Orchestrates the full lifecycle:
    1. Workspace & Target validation.
    2. Activity type classification.
    3. Initial PENDING record creation and persistence.
    4. Scope Authorization Gateway check.
    5. State transition to DENIED (if unauthorized) or AUTHORIZED (if authorized).
    6. Executor lookup and execution (RUNNING -> COMPLETED / FAILED).
    Returns (SecurityOperation, HTTP_STATUS_CODE).
    """
    # 1. Validate Workspace
    workspace = get_workspace(db, schema.workspace_id)
    if not workspace:
        raise ValueError(f"Workspace with ID '{schema.workspace_id}' does not exist.")

    # 2. Validate Target and Workspace alignment
    target = get_target(db, schema.target_id)
    if not target:
        raise ValueError(f"Target with ID '{schema.target_id}' does not exist.")
    if target.workspace_id != schema.workspace_id:
        raise ValueError(f"Target with ID '{schema.target_id}' does not belong to workspace '{schema.workspace_id}'.")

    # 3. Classify operation activity type
    activity_type = classify_operation_activity(schema.operation_type)

    # 4. Create initial PENDING record and persist
    db_op = SecurityOperation(
        workspace_id=schema.workspace_id,
        target_id=schema.target_id,
        operation_type=schema.operation_type,
        activity_type=activity_type,
        status=SecurityOperationStatus.PENDING,
        parameters=schema.parameters,
        requested_at=datetime.now(timezone.utc),
    )
    db.add(db_op)
    db.commit()
    db.refresh(db_op)

    # 5. Call Authorization Gateway
    auth_result = authorize_security_operation(
        db=db,
        workspace_id=schema.workspace_id,
        target=target,
        operation_type=schema.operation_type,
    )

    db_op.authorization_level = auth_result.authorization_level
    db_op.authorization_reason = auth_result.reason

    # 6. Handle Authorization DENIED
    if not auth_result.authorized:
        db_op.status = SecurityOperationStatus.DENIED
        db.commit()
        db.refresh(db_op)
        return (db_op, status.HTTP_403_FORBIDDEN)

    # 7. Authorization Approved -> AUTHORIZED
    db_op.status = SecurityOperationStatus.AUTHORIZED
    db.commit()
    db.refresh(db_op)

    # 8. Look up Executor
    executor = get_executor(schema.operation_type)
    if not executor:
        db_op.status = SecurityOperationStatus.FAILED
        db_op.error_message = f"No executor implemented for operation type: {schema.operation_type.value}"
        db.commit()
        db.refresh(db_op)
        return (db_op, status.HTTP_501_NOT_IMPLEMENTED)

    # 9. Transition to RUNNING and Execute
    db_op.status = SecurityOperationStatus.RUNNING
    db_op.started_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_op)

    try:
        result_data = executor.execute(target=target, parameters=schema.parameters)
        db_op.status = SecurityOperationStatus.COMPLETED
        db_op.result = result_data
        db_op.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_op)
        return (db_op, status.HTTP_201_CREATED)
    except Exception as err:
        db.rollback()
        # Re-query db_op if rollback cleared session state
        db_op = db.get(SecurityOperation, db_op.id)
        db_op.status = SecurityOperationStatus.FAILED
        db_op.error_message = str(err)
        db_op.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_op)
        return (db_op, status.HTTP_500_INTERNAL_SERVER_ERROR)
