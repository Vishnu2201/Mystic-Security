from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.authorization import AuthorizationCheckRequest, AuthorizationCheckResponse
from app.services import authorization_service

router = APIRouter()


@router.post(
    "/check",
    response_model=AuthorizationCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check Security Operation Authorization",
)
def check_authorization(
    payload: AuthorizationCheckRequest,
    db: Session = Depends(get_db),
) -> AuthorizationCheckResponse:
    """
    Verify whether a security operation is authorized for a target within a workspace.
    Returns HTTP 200 OK with a structured decision (authorized: true/false).
    Returns HTTP 404 Not Found if target does not exist or does not belong to specified workspace.
    Returns HTTP 422 Unprocessable Entity for invalid request payloads.
    """
    try:
        return authorization_service.authorize_security_operation(
            db=db,
            workspace_id=payload.workspace_id,
            target=payload.target_id,
            operation_type=payload.operation_type,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )
