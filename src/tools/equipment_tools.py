import logging
import traceback
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_equipment_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register equipment-related tools with the MCP server.

    Equipment corresponds to Mealie's "tools" organizer
    (`/api/organizers/tools`), exposed here as "equipment" to avoid
    overloading "tool" with MCP tools.
    """

    @mcp.tool()
    def get_equipment(
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all recipe equipment items with pagination.

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            search: Search term to filter equipment

        Returns:
            Dict[str, Any]: Equipment items with pagination information
        """
        try:
            logger.info(
                {
                    "message": "Fetching equipment",
                    "page": page,
                    "per_page": per_page,
                    "search": search,
                }
            )
            return mealie.get_equipment_list(page=page, per_page=per_page, search=search)
        except Exception as e:
            error_msg = f"Error fetching equipment: {str(e)}"
            logger.error({"message": error_msg})
            logger.debug({"message": "Error traceback", "traceback": traceback.format_exc()})
            raise ToolError(error_msg)

    @mcp.tool()
    def get_equipment_by_slug(equipment_slug: str) -> Dict[str, Any]:
        """Get a specific equipment item by its slug.

        Args:
            equipment_slug: The slug of the equipment (e.g., "stand-mixer")

        Returns:
            Dict[str, Any]: The equipment details
        """
        try:
            logger.info(
                {"message": "Fetching equipment by slug", "equipment_slug": equipment_slug}
            )
            return mealie.get_equipment_by_slug(equipment_slug)
        except Exception as e:
            error_msg = f"Error fetching equipment by slug '{equipment_slug}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug({"message": "Error traceback", "traceback": traceback.format_exc()})
            raise ToolError(error_msg)
