from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.enums import SecurityOperationStatus, SecurityOperationType
from app.schemas.security_operation import SecurityOperationCreate, SecurityOperationResponse
from app.services import security_operation_service

router = APIRouter()


@router.post(
    "",
    response_model=SecurityOperationResponse,
    summary="Create and Execute a Security Operation",
)
def create_security_operation(
    payload: SecurityOperationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new Security Operation, evaluate authorization against the Target Scope Engine,
    and execute supported operations (e.g. PASSIVE_RECON).
    
    Status Codes:
    - 201 Created: Authorized and successfully executed (status: COMPLETED).
    - 403 Forbidden: Scope authorization denied (status: DENIED, persisted).
    - 404 Not Found: Target missing or Workspace/Target mismatch.
    - 422 Unprocessable Entity: Invalid payload or operation_type enum.
    - 501 Not Implemented: Operation authorized but no executor implemented (status: FAILED, persisted).
    - 500 Internal Server Error: Execution error during operation (status: FAILED, persisted).
    """
    try:
        op, http_status = security_operation_service.create_and_execute_security_operation(
            db=db,
            schema=payload,
        )
        response_data = jsonable_encoder(SecurityOperationResponse.model_validate(op))
        return JSONResponse(status_code=http_status, content=response_data)
    except ValueError as err:
        msg = str(err)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg,
        )


@router.get(
    "",
    response_model=List[SecurityOperationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Security Operations",
)
def list_security_operations(
    workspace_id: Optional[UUID] = Query(None, description="Optional workspace ID filter"),
    target_id: Optional[UUID] = Query(None, description="Optional target ID filter"),
    operation_type: Optional[SecurityOperationType] = Query(None, description="Optional operation type filter"),
    status_filter: Optional[SecurityOperationStatus] = Query(None, alias="status", description="Optional status filter"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
    db: Session = Depends(get_db),
) -> List[SecurityOperationResponse]:
    """
    Retrieve a paginated list of security operations, with optional filtering by workspace_id, target_id, operation_type, or status.
    """
    return security_operation_service.list_security_operations(
        db=db,
        workspace_id=workspace_id,
        target_id=target_id,
        operation_type=operation_type,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{operation_id}",
    response_model=SecurityOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Security Operation by ID",
)
def get_security_operation(
    operation_id: UUID,
    db: Session = Depends(get_db),
) -> SecurityOperationResponse:
    """
    Retrieve details of a single security operation execution record.
    """
    op = security_operation_service.get_security_operation(db=db, operation_id=operation_id)
    if not op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security operation with ID '{operation_id}' not found.",
        )
    return op
