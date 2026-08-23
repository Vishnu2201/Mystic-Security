import ipaddress
import socket
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from app.models.enums import TargetCategory
from app.models.target import Target
from app.security_operations.base import BaseOperationExecutor


class PassiveReconExecutor(BaseOperationExecutor):
    """
    Real PASSIVE_RECON Security Operation Executor (Phase 0.9).
    Performs passive information gathering without active vulnerability scanning.
    - DOMAIN: DNS resolution using socket.getaddrinfo().
    - IP_ADDRESS: Reverse DNS lookup using socket.gethostbyaddr().
    - URL: URL host parsing and DNS resolution.
    - NETWORK_RANGE: CIDR metadata processing.
    - APPLICATION: Not supported.
    """

    def execute(self, target: Target, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        category = target.target_category

        if category == TargetCategory.DOMAIN:
            return self._execute_domain(target.identifier)

        elif category == TargetCategory.IP_ADDRESS:
            return self._execute_ip(target.identifier)

        elif category == TargetCategory.URL:
            return self._execute_url(target.identifier)

        elif category == TargetCategory.NETWORK_RANGE:
            return self._execute_network_range(target.identifier)

        elif category == TargetCategory.APPLICATION:
            raise ValueError("PASSIVE_RECON is not supported for APPLICATION target category")

        else:
            raise ValueError(f"Unsupported target category '{category}' for PASSIVE_RECON")

    def _execute_domain(self, domain_identifier: str) -> Dict[str, Any]:
        hostname = domain_identifier.strip().lower()
        try:
            info = socket.getaddrinfo(hostname, None)
            addresses = []
            seen = set()
            for item in info:
                family = "IPv4" if item[0] == socket.AF_INET else ("IPv6" if item[0] == socket.AF_INET6 else str(item[0]))
                addr = item[4][0]
                if (addr, family) not in seen:
                    seen.add((addr, family))
                    addresses.append({"address": addr, "family": family})
            return {
                "hostname": hostname,
                "addresses": addresses,
            }
        except Exception as err:
            return {
                "hostname": hostname,
                "addresses": [],
                "error": f"DNS resolution failed: {str(err)}",
            }

    def _execute_ip(self, ip_identifier: str) -> Dict[str, Any]:
        cleaned_ip = ip_identifier.strip()
        try:
            host_info = socket.gethostbyaddr(cleaned_ip)
            return {
                "ip_address": cleaned_ip,
                "reverse_dns": host_info[0],
                "aliases": list(host_info[1]) if host_info[1] else [],
            }
        except Exception as err:
            return {
                "ip_address": cleaned_ip,
                "reverse_dns": None,
                "error": f"Reverse DNS lookup failed: {str(err)}",
            }

    def _execute_url(self, url_identifier: str) -> Dict[str, Any]:
        cleaned_url = url_identifier.strip()
        try:
            parsed = urlparse(cleaned_url)
            hostname = parsed.hostname or ""
            if not hostname:
                raise ValueError("URL host component could not be parsed.")

            info = socket.getaddrinfo(hostname, None)
            addresses = []
            seen = set()
            for item in info:
                family = "IPv4" if item[0] == socket.AF_INET else ("IPv6" if item[0] == socket.AF_INET6 else str(item[0]))
                addr = item[4][0]
                if (addr, family) not in seen:
                    seen.add((addr, family))
                    addresses.append({"address": addr, "family": family})
            return {
                "url": cleaned_url,
                "hostname": hostname,
                "addresses": addresses,
            }
        except Exception as err:
            return {
                "url": cleaned_url,
                "hostname": parsed.hostname if 'parsed' in locals() and parsed else "",
                "addresses": [],
                "error": f"URL hostname resolution failed: {str(err)}",
            }

    def _execute_network_range(self, cidr_identifier: str) -> Dict[str, Any]:
        cleaned_cidr = cidr_identifier.strip()
        try:
            net = ipaddress.ip_network(cleaned_cidr, strict=False)
            return {
                "network": str(net.network_address),
                "prefix_length": net.prefixlen,
                "address_count": net.num_addresses,
                "netmask": str(net.netmask),
                "broadcast_address": str(net.broadcast_address),
            }
        except Exception as err:
            return {
                "network_range": cleaned_cidr,
                "error": f"Network metadata processing failed: {str(err)}",
            }
