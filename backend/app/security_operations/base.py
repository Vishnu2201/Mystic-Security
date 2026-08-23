from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.models.target import Target


class BaseOperationExecutor(ABC):
    """
    Abstract Base Class for Security Operation Executors (Phase 0.9).
    Defines common execution contract for scanners, recon tools, and security operations.
    """

    @abstractmethod
    def execute(self, target: Target, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute security operation against the target.
        Must return a structured dictionary containing real empirical execution output.
        """
        pass
