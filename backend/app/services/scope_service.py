import ipaddress
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.scope import Scope
from app.models.enums import ActivityType, AuthorizationLevel, ScopeType, TargetCategory
from app.schemas.scope import ScopeCreate, ScopeUpdate, TargetAuthorizationResult
from app.services.workspace_service import get_workspace
from app.core.validators import (
    validate_workspace_name,
    validate_workspace_description,
    validate_target_identifier,
)


def get_scope(db: Session, scope_id: UUID) -> Optional[Scope]:
    """Retrieve a single scope by its primary key UUID."""
    return db.get(Scope, scope_id)


def get_scope_by_pattern(
    db: Session,
    workspace_id: UUID,
    scope_type: ScopeType,
    pattern: str,
) -> Optional[Scope]:
    """Retrieve a scope by unique workspace ID, scope type, and pattern combination."""
    stmt = select(Scope).where(
        Scope.workspace_id == workspace_id,
        Scope.scope_type == scope_type,
        Scope.pattern == pattern,
    )
    return db.scalar(stmt)


def list_scopes(
    db: Session,
    workspace_id: Optional[UUID] = None,
    scope_type: Optional[ScopeType] = None,
    authorization_level: Optional[AuthorizationLevel] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Scope]:
    """List scopes with optional filtering and pagination support."""
    stmt = select(Scope)
    if workspace_id is not None:
        stmt = stmt.where(Scope.workspace_id == workspace_id)
    if scope_type is not None:
        stmt = stmt.where(Scope.scope_type == scope_type)
    if authorization_level is not None:
        stmt = stmt.where(Scope.authorization_level == authorization_level)
    if is_active is not None:
        stmt = stmt.where(Scope.is_active == is_active)

    stmt = stmt.order_by(Scope.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_scope(db: Session, schema: ScopeCreate) -> Scope:
    """Create a new Scope entity within an existing Workspace."""
    workspace = get_workspace(db, schema.workspace_id)
    if not workspace:
        raise ValueError(f"Workspace with ID '{schema.workspace_id}' does not exist.")

    # Syntactically validate name, description, and pattern against scope_type
    clean_name = validate_workspace_name(schema.name)
    clean_desc = validate_workspace_description(schema.description)
    clean_pattern = validate_target_identifier(schema.scope_type, schema.pattern)

    # Check workspace-scoped duplicate (workspace_id, scope_type, pattern)
    existing = get_scope_by_pattern(db, schema.workspace_id, schema.scope_type, clean_pattern)
    if existing:
        raise ValueError(
            f"Scope with type '{schema.scope_type}' and pattern '{clean_pattern}' already exists in workspace '{schema.workspace_id}'."
        )

    db_scope = Scope(
        workspace_id=schema.workspace_id,
        name=clean_name,
        description=clean_desc,
        scope_type=schema.scope_type,
        pattern=clean_pattern,
        authorization_level=schema.authorization_level,
        is_active=schema.is_active,
    )
    try:
        db.add(db_scope)
        db.commit()
        db.refresh(db_scope)
        return db_scope
    except IntegrityError as err:
        db.rollback()
        raise ValueError(
            f"Scope with type '{schema.scope_type}' and pattern '{clean_pattern}' already exists in workspace '{schema.workspace_id}'."
        ) from err


def update_scope(db: Session, db_scope: Scope, schema: ScopeUpdate) -> Scope:
    """
    Update an existing Scope entity using partial model data.
    Evaluates final effective (workspace_id, scope_type, pattern) combination
    before mutation to ensure syntactic validity and uniqueness collision detection.
    """
    # 1. Evaluate effective workspace_id
    effective_workspace_id = db_scope.workspace_id
    if "workspace_id" in schema.model_fields_set:
        if schema.workspace_id is None:
            raise ValueError("Scope workspace_id cannot be null.")
        if schema.workspace_id != db_scope.workspace_id:
            workspace = get_workspace(db, schema.workspace_id)
            if not workspace:
                raise ValueError(f"Workspace with ID '{schema.workspace_id}' does not exist.")
            effective_workspace_id = schema.workspace_id

    # 2. Evaluate effective scope_type and pattern
    effective_type = db_scope.scope_type
    if "scope_type" in schema.model_fields_set:
        if schema.scope_type is None:
            raise ValueError("Scope scope_type cannot be null.")
        effective_type = schema.scope_type

    effective_pattern = db_scope.pattern
    if "pattern" in schema.model_fields_set:
        if schema.pattern is None:
            raise ValueError("Scope pattern cannot be null.")
        effective_pattern = schema.pattern

    # 3. Validate effective pattern against effective scope_type if either changed
    if "scope_type" in schema.model_fields_set or "pattern" in schema.model_fields_set:
        effective_pattern = validate_target_identifier(effective_type, effective_pattern)

    # 4. Check uniqueness collision for effective (workspace_id, scope_type, pattern)
    if (
        effective_workspace_id != db_scope.workspace_id
        or effective_type != db_scope.scope_type
        or effective_pattern != db_scope.pattern
    ):
        existing = get_scope_by_pattern(db, effective_workspace_id, effective_type, effective_pattern)
        if existing and existing.id != db_scope.id:
            raise ValueError(
                f"Scope with type '{effective_type}' and pattern '{effective_pattern}' already exists in workspace '{effective_workspace_id}'."
            )

    # 5. Apply mutations
    if "workspace_id" in schema.model_fields_set:
        db_scope.workspace_id = effective_workspace_id

    if "name" in schema.model_fields_set:
        db_scope.name = validate_workspace_name(schema.name)

    if "description" in schema.model_fields_set:
        db_scope.description = validate_workspace_description(schema.description)

    if "scope_type" in schema.model_fields_set:
        db_scope.scope_type = effective_type

    if "identifier" in schema.model_fields_set or "pattern" in schema.model_fields_set:
        db_scope.pattern = effective_pattern

    if "authorization_level" in schema.model_fields_set:
        if schema.authorization_level is None:
            raise ValueError("Scope authorization_level cannot be null.")
        db_scope.authorization_level = schema.authorization_level

    if "is_active" in schema.model_fields_set:
        if schema.is_active is None:
            raise ValueError("Scope is_active cannot be null.")
        db_scope.is_active = schema.is_active

    try:
        db.commit()
        db.refresh(db_scope)
        return db_scope
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Scope update failed due to database constraint violation.") from err


def delete_scope(db: Session, db_scope: Scope) -> None:
    """Delete an existing Scope entity."""
    try:
        db.delete(db_scope)
        db.commit()
    except Exception:
        db.rollback()
        raise


def _match_domain(target_identifier: str, scope_pattern: str) -> bool:
    """
    Domain matching rule:
    Target 'example.com' or 'api.example.com' matches scope 'example.com'.
    Target 'notexample.com' or 'example.com.attacker.com' does NOT match scope 'example.com'.
    """
    target = target_identifier.strip().lower()
    scope = scope_pattern.strip().lower()
    if target == scope:
        return True
    if target.endswith("." + scope):
        return True
    return False


def is_target_authorized(
    db: Session,
    workspace_id: UUID,
    target_category: TargetCategory,
    identifier: str,
    activity_type: ActivityType,
) -> TargetAuthorizationResult:
    """
    Target Authorization Check Engine for Phase 0.7.
    Evaluates whether security activity (PASSIVE or ACTIVE) is authorized for a given target.
    
    Priority Rules:
    1. PROHIBITED takes highest priority -> DENY.
    2. ACTIVE_ALLOWED takes priority over PASSIVE_ONLY -> ALLOW for PASSIVE and ACTIVE.
    3. PASSIVE_ONLY -> ALLOW for PASSIVE, DENY for ACTIVE.
    4. Inactive scopes are ignored.
    5. Default behavior -> DENY.
    """
    # Load all active scopes belonging to the workspace
    stmt = select(Scope).where(Scope.workspace_id == workspace_id, Scope.is_active == True)
    active_scopes = list(db.scalars(stmt).all())

    matched_scopes: List[Scope] = []
    clean_identifier = identifier.strip()

    for scope in active_scopes:
        matched = False
        if target_category == TargetCategory.DOMAIN and scope.scope_type == ScopeType.DOMAIN:
            matched = _match_domain(clean_identifier, scope.pattern)

        elif target_category == TargetCategory.URL and scope.scope_type == ScopeType.URL:
            matched = (clean_identifier == scope.pattern.strip())

        elif target_category == TargetCategory.IP_ADDRESS:
            if scope.scope_type == ScopeType.IP_ADDRESS:
                matched = (clean_identifier == scope.pattern.strip())
            elif scope.scope_type == ScopeType.NETWORK_RANGE:
                try:
                    target_ip = ipaddress.ip_address(clean_identifier)
                    scope_net = ipaddress.ip_network(scope.pattern.strip(), strict=False)
                    matched = (target_ip in scope_net)
                except ValueError:
                    matched = False

        elif target_category == TargetCategory.NETWORK_RANGE:
            if scope.scope_type == ScopeType.NETWORK_RANGE:
                try:
                    target_net = ipaddress.ip_network(clean_identifier, strict=False)
                    scope_net = ipaddress.ip_network(scope.pattern.strip(), strict=False)
                    matched = target_net.subnet_of(scope_net)
                except ValueError:
                    matched = False

        elif target_category == TargetCategory.APPLICATION and scope.scope_type == ScopeType.APPLICATION:
            matched = (clean_identifier == scope.pattern.strip())

        if matched:
            matched_scopes.append(scope)

    if not matched_scopes:
        return TargetAuthorizationResult(
            authorized=False,
            authorization_level=None,
            matched_scope_id=None,
            reason="No matching active scope found for workspace (default deny)",
        )

    # 1. Highest Priority: PROHIBITED
    prohibited_scope = next((s for s in matched_scopes if s.authorization_level == AuthorizationLevel.PROHIBITED), None)
    if prohibited_scope:
        return TargetAuthorizationResult(
            authorized=False,
            authorization_level=AuthorizationLevel.PROHIBITED,
            matched_scope_id=prohibited_scope.id,
            reason="Target matches a PROHIBITED scope",
        )

    # 2. Second Priority: ACTIVE_ALLOWED
    active_scope = next((s for s in matched_scopes if s.authorization_level == AuthorizationLevel.ACTIVE_ALLOWED), None)
    if active_scope:
        return TargetAuthorizationResult(
            authorized=True,
            authorization_level=AuthorizationLevel.ACTIVE_ALLOWED,
            matched_scope_id=active_scope.id,
            reason="Target matches an ACTIVE_ALLOWED scope",
        )

    # 3. Third Priority: PASSIVE_ONLY
    passive_scope = next((s for s in matched_scopes if s.authorization_level == AuthorizationLevel.PASSIVE_ONLY), None)
    if passive_scope:
        if activity_type == ActivityType.PASSIVE:
            return TargetAuthorizationResult(
                authorized=True,
                authorization_level=AuthorizationLevel.PASSIVE_ONLY,
                matched_scope_id=passive_scope.id,
                reason="Target matches a PASSIVE_ONLY scope for PASSIVE activity",
            )
        else:
            return TargetAuthorizationResult(
                authorized=False,
                authorization_level=AuthorizationLevel.PASSIVE_ONLY,
                matched_scope_id=passive_scope.id,
                reason="Target matches a PASSIVE_ONLY scope but ACTIVE activity was requested",
            )

    return TargetAuthorizationResult(
        authorized=False,
        authorization_level=None,
        matched_scope_id=None,
        reason="No matching active scope found for workspace (default deny)",
    )
