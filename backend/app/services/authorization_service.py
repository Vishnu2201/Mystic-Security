from typing import Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.enums import AuthorizationLevel, SecurityOperationType
from app.models.target import Target
from app.schemas.authorization import AuthorizationCheckResponse
from app.services.target_service import get_target
from app.services.scope_service import is_target_authorized
from app.core.authorization import classify_operation_activity


def authorize_security_operation(
    db: Session,
    workspace_id: UUID,
    target: Union[Target, UUID],
    operation_type: SecurityOperationType,
) -> AuthorizationCheckResponse:
    """
    Central Authorization Gateway for Security Operations (Phase 0.8).
    Evaluates whether a requested security operation against a target is authorized.
    
    Guarantees:
    1. Target existence and workspace alignment.
    2. Operation activity type classification (PASSIVE vs ACTIVE).
    3. Scope authorization engine evaluation.
    4. Fail-closed default deny on any invalid input or evaluation error.
    """
    # 1. Resolve Target instance and verify workspace alignment
    if isinstance(target, UUID):
        target_obj = get_target(db, target)
        if not target_obj:
            raise ValueError(f"Target with ID '{target}' not found.")
    else:
        target_obj = target

    if target_obj.workspace_id != workspace_id:
        raise ValueError(f"Target with ID '{target_obj.id}' does not belong to workspace '{workspace_id}'.")

    # 2. Classify operation activity type (PASSIVE vs ACTIVE)
    try:
        activity_type = classify_operation_activity(operation_type)
    except ValueError as err:
        return AuthorizationCheckResponse(
            authorized=False,
            workspace_id=workspace_id,
            target_id=target_obj.id,
            operation_type=operation_type,
            activity_type=None,
            authorization_level=None,
            reason=str(err),
        )

    # 3. Evaluate scope authorization engine
    try:
        scope_result = is_target_authorized(
            db=db,
            workspace_id=workspace_id,
            target_category=target_obj.target_category,
            identifier=target_obj.identifier,
            activity_type=activity_type,
        )

        if scope_result.authorized:
            reason = f"Operation '{operation_type.value}' ({activity_type.value}) is permitted by {scope_result.authorization_level.value} scope"
        else:
            if scope_result.authorization_level == AuthorizationLevel.PASSIVE_ONLY:
                reason = f"Operation '{operation_type.value}' requires ACTIVE authorization but matching scope allows PASSIVE_ONLY"
            elif scope_result.authorization_level == AuthorizationLevel.PROHIBITED:
                reason = "Matching scope is PROHIBITED"
            else:
                reason = scope_result.reason

        return AuthorizationCheckResponse(
            authorized=scope_result.authorized,
            workspace_id=workspace_id,
            target_id=target_obj.id,
            operation_type=operation_type,
            activity_type=activity_type,
            authorization_level=scope_result.authorization_level,
            reason=reason,
        )
    except Exception:
        return AuthorizationCheckResponse(
            authorized=False,
            workspace_id=workspace_id,
            target_id=target_obj.id,
            operation_type=operation_type,
            activity_type=activity_type,
            authorization_level=None,
            reason="Authorization evaluation failed (default deny)",
        )


def require_operation_authorization(
    db: Session,
    workspace_id: UUID,
    target_id: UUID,
    operation_type: SecurityOperationType,
) -> AuthorizationCheckResponse:
    """
    Enforcement helper for future execution endpoints.
    Verifies authorization before operation execution.
    - If authorized: returns AuthorizationCheckResponse.
    - If denied: raises HTTP 403 Forbidden.
    - If target missing or workspace mismatch: raises HTTP 404 Not Found.
    """
    try:
        result = authorize_security_operation(
            db=db,
            workspace_id=workspace_id,
            target=target_id,
            operation_type=operation_type,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )

    if not result.authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=result.reason,
        )

    return result
