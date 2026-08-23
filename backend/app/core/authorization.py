from app.models.enums import ActivityType, SecurityOperationType


def classify_operation_activity(operation_type: SecurityOperationType) -> ActivityType:
    """
    Classify a SecurityOperationType into its corresponding ActivityType (PASSIVE or ACTIVE).
    Reusable classification logic independent of API routers.
    """
    if operation_type == SecurityOperationType.PASSIVE_RECON:
        return ActivityType.PASSIVE
    elif operation_type in (
        SecurityOperationType.ACTIVE_RECON,
        SecurityOperationType.PORT_SCAN,
        SecurityOperationType.VULNERABILITY_SCAN,
        SecurityOperationType.WEB_SCAN,
        SecurityOperationType.CUSTOM,
    ):
        return ActivityType.ACTIVE
    else:
        raise ValueError(f"Unsupported security operation type '{operation_type}' (default deny)")
