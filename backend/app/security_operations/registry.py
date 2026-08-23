from typing import Dict, Optional
from app.models.enums import SecurityOperationType
from app.security_operations.base import BaseOperationExecutor
from app.security_operations.passive_recon import PassiveReconExecutor

# Executor Registry mapping SecurityOperationType to executor instance
EXECUTOR_REGISTRY: Dict[SecurityOperationType, BaseOperationExecutor] = {
    SecurityOperationType.PASSIVE_RECON: PassiveReconExecutor(),
}


def get_executor(operation_type: SecurityOperationType) -> Optional[BaseOperationExecutor]:
    """
    Look up an operation executor by SecurityOperationType.
    Returns BaseOperationExecutor instance or None if no executor is implemented.
    """
    return EXECUTOR_REGISTRY.get(operation_type)
