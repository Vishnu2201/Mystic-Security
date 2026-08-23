from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.services import workspace_service

router = APIRouter()


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Workspace",
)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """
    Create a new organizational workspace isolation boundary.
    """
    try:
        return workspace_service.create_workspace(db=db, schema=payload)
    except ValueError as err:
        msg = str(err)
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
    response_model=List[WorkspaceResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Workspaces",
)
def list_workspaces(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    """
    Retrieve a paginated list of workspaces.
    Returns an empty array when no workspaces exist in the database.
    """
    return workspace_service.list_workspaces(db=db, skip=skip, limit=limit)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Workspace by ID",
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """
    Retrieve a single workspace by its unique identifier.
    """
    db_workspace = workspace_service.get_workspace(db=db, workspace_id=workspace_id)
    if not db_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID '{workspace_id}' not found.",
        )
    return db_workspace


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Workspace",
)
def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """
    Update details of an existing workspace.
    """
    db_workspace = workspace_service.get_workspace(db=db, workspace_id=workspace_id)
    if not db_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID '{workspace_id}' not found.",
        )
    try:
        return workspace_service.update_workspace(db=db, db_workspace=db_workspace, schema=payload)
    except ValueError as err:
        msg = str(err)
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
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Workspace",
)
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an existing workspace and its associated resources.
    """
    db_workspace = workspace_service.get_workspace(db=db, workspace_id=workspace_id)
    if not db_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID '{workspace_id}' not found.",
        )
    workspace_service.delete_workspace(db=db, db_workspace=db_workspace)
