from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.target import TargetCreate, TargetResponse, TargetUpdate
from app.services import target_service

router = APIRouter()


@router.post(
    "",
    response_model=TargetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Target",
)
def create_target(
    payload: TargetCreate,
    db: Session = Depends(get_db),
) -> TargetResponse:
    """
    Create a new empirical target subject within a Workspace.
    """
    try:
        return target_service.create_target(db=db, schema=payload)
    except ValueError as err:
        msg = str(err)
        if "does not exist" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg,
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg,
        )


@router.get(
    "",
    response_model=List[TargetResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Targets",
)
def list_targets(
    workspace_id: Optional[UUID] = Query(None, description="Optional workspace ID filter"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
    db: Session = Depends(get_db),
) -> List[TargetResponse]:
    """
    Retrieve a paginated list of targets, optionally filtered by workspace_id.
    Returns an empty array when no targets exist matching the filter.
    """
    return target_service.list_targets(
        db=db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{target_id}",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Target by ID",
)
def get_target(
    target_id: UUID,
    db: Session = Depends(get_db),
) -> TargetResponse:
    """
    Retrieve a single target by its unique identifier.
    """
    db_target = target_service.get_target(db=db, target_id=target_id)
    if not db_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' not found.",
        )
    return db_target


@router.patch(
    "/{target_id}",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Target",
)
def update_target(
    target_id: UUID,
    payload: TargetUpdate,
    db: Session = Depends(get_db),
) -> TargetResponse:
    """
    Update details of an existing target.
    """
    db_target = target_service.get_target(db=db, target_id=target_id)
    if not db_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' not found.",
        )
    try:
        return target_service.update_target(db=db, db_target=db_target, schema=payload)
    except ValueError as err:
        msg = str(err)
        if "does not exist" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg,
            )
        if "cannot be null" in msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=msg,
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg,
        )


@router.delete(
    "/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Target",
)
def delete_target(
    target_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an existing target.
    """
    db_target = target_service.get_target(db=db, target_id=target_id)
    if not db_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' not found.",
        )
    try:
        target_service.delete_target(db=db, db_target=db_target)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        )
