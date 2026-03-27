"""
API for managing Databricks Delta Sharing shares.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.utils import DatabricksAPIError, make_api_request

logger = logging.getLogger(__name__)


async def list_shares() -> Dict[str, Any]:
    """
    List all Delta Sharing shares.

    Returns:
        Response containing a list of shares.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Listing shares")
    return make_api_request("GET", "/api/2.1/unity-catalog/shares")


async def create_share(name: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new Delta Sharing share.

    Args:
        name: Name of the share (must be unique within the metastore)
        comment: Optional comment / description

    Returns:
        Response containing the created share object.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Creating share: {name}")
    data: Dict[str, Any] = {"name": name}
    if comment is not None:
        data["comment"] = comment
    return make_api_request("POST", "/api/2.1/unity-catalog/shares", data=data)


async def get_share(name: str, include_shared_data: bool = False) -> Dict[str, Any]:
    """
    Get details of a Delta Sharing share.

    Args:
        name: Name of the share
        include_shared_data: If True, include the list of shared objects in the response

    Returns:
        Response containing the share object.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting share: {name}")
    return make_api_request(
        "GET",
        f"/api/2.1/unity-catalog/shares/{name}",
        params={"include_shared_data": str(include_shared_data).lower()},
    )


async def update_share(name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a Delta Sharing share.

    Args:
        name: Name of the share to update
        updates: Dict of fields to update, e.g.:
                 - new_name: str — rename the share
                 - comment: str — update description
                 - updates: list of {action: "ADD"|"REMOVE", data_object: {...}}
                   to add or remove shared objects (tables, schemas, volumes)

    Returns:
        Response containing the updated share object.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Updating share: {name}")
    return make_api_request("PATCH", f"/api/2.1/unity-catalog/shares/{name}", data=updates)


async def delete_share(name: str) -> Dict[str, Any]:
    """
    Delete a Delta Sharing share.

    Args:
        name: Name of the share to delete

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting share: {name}")
    return make_api_request("DELETE", f"/api/2.1/unity-catalog/shares/{name}")


async def get_share_permissions(name: str) -> Dict[str, Any]:
    """
    Get the permissions of a Delta Sharing share.

    Args:
        name: Name of the share

    Returns:
        Response containing the list of privilege assignments.

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting permissions for share: {name}")
    return make_api_request("GET", f"/api/2.1/unity-catalog/shares/{name}/permissions")


async def update_share_permissions(
    name: str, changes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update the permissions of a Delta Sharing share.

    Args:
        name: Name of the share
        changes: List of permission changes, each with:
                 - principal: str (user email or group name)
                 - add: list of privilege strings to grant (e.g. ["SELECT"])
                 - remove: list of privilege strings to revoke

    Returns:
        Empty response on success

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Updating permissions for share: {name}")
    return make_api_request(
        "PATCH",
        f"/api/2.1/unity-catalog/shares/{name}/permissions",
        data={"changes": changes},
    )
