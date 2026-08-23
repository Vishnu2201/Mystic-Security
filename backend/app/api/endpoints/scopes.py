from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.enums import AuthorizationLevel, ScopeType
from app.schemas.scope import ScopeCreate, ScopeResponse, ScopeUpdate
from app.services import scope_service

router = APIRouter()


@router.post(
    "",
    response_model=ScopeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Scope",
)
def create_scope(
    payload: ScopeCreate,
    db: Session = Depends(get_db),
) -> ScopeResponse:
    """
    Create a new target inclusion, exclusion, or authorization Scope rule.
    """
    try:
        return scope_service.create_scope(db=db, schema=payload)
    except ValueError as err:
        msg = str(err)
        if "does not exist" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg,
            )
        if "already exists" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=msg,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=msg,
        )


@router.get(
    "",
    response_model=List[ScopeResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Scopes",
)
def list_scopes(
    workspace_id: Optional[UUID] = Query(None, description="Optional workspace ID filter"),
    scope_type: Optional[ScopeType] = Query(None, description="Optional scope type filter"),
    authorization_level: Optional[AuthorizationLevel] = Query(None, description="Optional authorization level filter"),
    is_active: Optional[bool] = Query(None, description="Optional active status filter"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
    db: Session = Depends(get_db),
) -> List[ScopeResponse]:
    """
    Retrieve a paginated list of scopes with optional filtering by workspace_id, scope_type, authorization_level, or is_active.
    """
    return scope_service.list_scopes(
        db=db,
        workspace_id=workspace_id,
        scope_type=scope_type,
        authorization_level=authorization_level,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{scope_id}",
    response_model=ScopeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Scope by ID",
)
def get_scope(
    scope_id: UUID,
    db: Session = Depends(get_db),
) -> ScopeResponse:
    """
    Retrieve a single scope by its unique identifier.
    """
    db_scope = scope_service.get_scope(db=db, scope_id=scope_id)
    if not db_scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scope with ID '{scope_id}' not found.",
        )
    return db_scope


@router.patch(
    "/{scope_id}",
    response_model=ScopeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Scope",
)
def update_scope(
    scope_id: UUID,
    payload: ScopeUpdate,
    db: Session = Depends(get_db),
) -> ScopeResponse:
    """
    Update details of an existing scope.
    """
    db_scope = scope_service.get_scope(db=db, scope_id=scope_id)
    if not db_scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scope with ID '{scope_id}' not found.",
        )
    try:
        return scope_service.update_scope(db=db, db_scope=db_scope, schema=payload)
    except ValueError as err:
        msg = str(err)
        if "does not exist" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg,
            )
        if "already exists" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=msg,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=msg,
        )


@router.delete(
    "/{scope_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Scope",
)
def delete_scope(
    scope_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an existing scope.
    """
    db_scope = scope_service.get_scope(db=db, scope_id=scope_id)
    if not db_scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scope with ID '{scope_id}' not found.",
        )
    scope_service.delete_scope(db=db, db_scope=db_scope)
