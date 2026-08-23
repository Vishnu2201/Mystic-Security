import enum


class TargetCategory(str, enum.Enum):
    DOMAIN = "DOMAIN"
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"
    NETWORK_RANGE = "NETWORK_RANGE"
    APPLICATION = "APPLICATION"


class ScopeType(str, enum.Enum):
    DOMAIN = "DOMAIN"
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"
    NETWORK_RANGE = "NETWORK_RANGE"
    APPLICATION = "APPLICATION"


class AuthorizationLevel(str, enum.Enum):
    PASSIVE_ONLY = "PASSIVE_ONLY"
    ACTIVE_ALLOWED = "ACTIVE_ALLOWED"
    PROHIBITED = "PROHIBITED"


class ActivityType(str, enum.Enum):
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"


class SecurityOperationType(str, enum.Enum):
    PASSIVE_RECON = "PASSIVE_RECON"
    ACTIVE_RECON = "ACTIVE_RECON"
    PORT_SCAN = "PORT_SCAN"
    VULNERABILITY_SCAN = "VULNERABILITY_SCAN"
    WEB_SCAN = "WEB_SCAN"
    CUSTOM = "CUSTOM"


class SecurityOperationStatus(str, enum.Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DENIED = "DENIED"


class AuthorizationStatus(str, enum.Enum):
    """
    Persisted lifecycle status for operational consent records.
    Note: EXPIRED is an effective runtime validity status evaluated from timestamp boundaries,
    not a persisted database state.
    """
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class ScopeRuleAction(str, enum.Enum):
    INCLUDE = "INCLUDE"
    EXCLUDE = "EXCLUDE"


class ScopeRuleCategory(str, enum.Enum):
    DOMAIN = "DOMAIN"
    SUBDOMAIN_PATTERN = "SUBDOMAIN_PATTERN"
    URL = "URL"
    IP_ADDRESS = "IP_ADDRESS"
    CIDR_RANGE = "CIDR_RANGE"
    APPLICATION = "APPLICATION"


class AssessmentMode(str, enum.Enum):
    FAST = "FAST"
    BALANCED = "BALANCED"
    THOROUGH = "THOROUGH"
    CUSTOM = "CUSTOM"


class AssessmentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AssetType(str, enum.Enum):
    DOMAIN = "DOMAIN"
    HOST = "HOST"
    IP_ADDRESS = "IP_ADDRESS"
    SERVICE = "SERVICE"
    APPLICATION = "APPLICATION"


class FindingSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    REMEDIATED = "REMEDIATED"
    ACCEPTED_RISK = "ACCEPTED_RISK"


class ReportStatus(str, enum.Enum):
    GENERATING = "GENERATING"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
