"""Read-only campaign projections and derived local coordination primitives.

Importing this package remains dependency-free.  FastMCP is imported only by
``orchestration.campaign.mcp_server`` when the optional daemon is started.
"""
from .lease import LeaseConflictError, LeaseError, LeaseManager, LeaseNotOwnedError
from .models import AgentPresence, ControllerLease
from .store import CampaignStore, CampaignStoreError

__all__ = [
    "AgentPresence",
    "CampaignStore",
    "CampaignStoreError",
    "ControllerLease",
    "LeaseConflictError",
    "LeaseError",
    "LeaseManager",
    "LeaseNotOwnedError",
]
