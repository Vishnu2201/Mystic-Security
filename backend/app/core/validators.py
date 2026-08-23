import ipaddress
import re
from typing import Optional
from urllib.parse import urlparse
from app.models.enums import TargetCategory

# Hostname / domain regex for DOMAIN target validation
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
)


def validate_workspace_name(name: Optional[str]) -> str:
    """
    Validate and normalize a workspace name.
    Leading and trailing whitespace is stripped.
    Raises ValueError if empty, whitespace-only, null, or exceeding 255 characters.
    """
    if name is None:
        raise ValueError("Workspace name cannot be null.")
    if not isinstance(name, str):
        raise ValueError("Workspace name must be a string.")

    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Workspace name cannot be empty or whitespace-only.")
    if len(cleaned_name) > 255:
        raise ValueError("Workspace name exceeds maximum length of 255 characters.")
    return cleaned_name


def validate_workspace_description(description: Optional[str]) -> Optional[str]:
    """Validate optional workspace description."""
    if description is None:
        return None
    if not isinstance(description, str):
        raise ValueError("Workspace description must be a string or null.")
    return description.strip()


def validate_target_identifier(category: TargetCategory, identifier: str) -> str:
    """
    Syntactically validate a target identifier against its TargetCategory.
    Returns normalized identifier string or raises ValueError.
    Does NOT perform network I/O, DNS resolution, or HTTP requests.
    """
    if not identifier or not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("Target identifier cannot be empty.")

    cleaned_identifier = identifier.strip()

    if category == TargetCategory.DOMAIN:
        # DOMAIN expects a pure hostname (e.g. example.com or sub.example.com)
        if "://" in cleaned_identifier:
            raise ValueError(
                f"Invalid DOMAIN identifier '{identifier}'. Domain targets must be hostnames without URL protocol schemes (e.g., use 'example.com' instead of '{identifier}')."
            )
        if "/" in cleaned_identifier or "?" in cleaned_identifier or "#" in cleaned_identifier or ":" in cleaned_identifier or " " in cleaned_identifier:
            raise ValueError(
                f"Invalid DOMAIN identifier '{identifier}'. Domain targets must not contain path components (/), query parameters, port numbers, or spaces."
            )
        
        normalized_domain = cleaned_identifier.lower()
        if not DOMAIN_REGEX.match(normalized_domain) and normalized_domain != "localhost":
            raise ValueError(
                f"Invalid DOMAIN identifier '{identifier}'. Must be a syntactically valid domain name (e.g., example.com)."
            )
        return normalized_domain

    elif category == TargetCategory.URL:
        # URL expects a valid HTTP or HTTPS URL (e.g. https://example.com/path)
        try:
            parsed = urlparse(cleaned_identifier)
        except Exception as err:
            raise ValueError(f"Invalid URL identifier '{identifier}'. URL parsing failed.") from err

        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"Invalid URL identifier '{identifier}'. URL targets must use 'http://' or 'https://' protocol schemes."
            )
        if not parsed.netloc:
            raise ValueError(
                f"Invalid URL identifier '{identifier}'. URL targets must include a valid host component."
            )
        return cleaned_identifier

    elif category == TargetCategory.IP_ADDRESS:
        # IP_ADDRESS expects a valid IPv4 or IPv6 address string
        try:
            ip_obj = ipaddress.ip_address(cleaned_identifier)
            return str(ip_obj)
        except ValueError as err:
            raise ValueError(
                f"Invalid IP_ADDRESS identifier '{identifier}'. Must be a valid IPv4 or IPv6 address."
            ) from err

    elif category == TargetCategory.NETWORK_RANGE:
        # NETWORK_RANGE expects a valid CIDR network range string
        try:
            net_obj = ipaddress.ip_network(cleaned_identifier, strict=False)
            return str(net_obj)
        except ValueError as err:
            raise ValueError(
                f"Invalid NETWORK_RANGE identifier '{identifier}'. Must be a valid CIDR network range (e.g., 192.168.1.0/24)."
            ) from err

    elif category == TargetCategory.APPLICATION:
        # APPLICATION expects a non-empty application name/identifier
        if len(cleaned_identifier) < 1:
            raise ValueError("APPLICATION identifier cannot be empty.")
        return cleaned_identifier

    return cleaned_identifier


def validate_ip_address(ip_address: Optional[str]) -> Optional[str]:
    """Validate optional standalone ip_address field."""
    if ip_address is None:
        return None
    if not isinstance(ip_address, str) or not ip_address.strip():
        raise ValueError("ip_address cannot be empty when provided.")
    try:
        ip_obj = ipaddress.ip_address(ip_address.strip())
        return str(ip_obj)
    except ValueError as err:
        raise ValueError(
            f"Invalid ip_address '{ip_address}'. Must be a valid IPv4 or IPv6 address."
        ) from err


def validate_network_range(network_range: Optional[str]) -> Optional[str]:
    """Validate optional standalone network_range CIDR field."""
    if network_range is None:
        return None
    if not isinstance(network_range, str) or not network_range.strip():
        raise ValueError("network_range cannot be empty when provided.")
    try:
        net_obj = ipaddress.ip_network(network_range.strip(), strict=False)
        return str(net_obj)
    except ValueError as err:
        raise ValueError(
            f"Invalid network_range '{network_range}'. Must be a valid CIDR network range (e.g., 192.168.1.0/24)."
        ) from err
