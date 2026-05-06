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

    @mcp.tool()
    def create_equipment(name: str) -> Dict[str, Any]:
        """Create a new equipment item.

        Use this when `set_recipe_equipment` reports an unknown equipment
        slug. Mealie's equipment schema only accepts a name — there is no
        plural form, description, or label, unlike foods.

        Args:
            name: Name of the equipment (e.g., "cast iron skillet", "sheet pan")

        Returns:
            Dict[str, Any]: The created equipment details, including id and slug
        """
        try:
            logger.info({"message": "Creating equipment", "name": name})
            return mealie.create_equipment(name)
        except Exception as e:
            error_msg = f"Error creating equipment '{name}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug({"message": "Error traceback", "traceback": traceback.format_exc()})
            raise ToolError(error_msg)

    @mcp.tool()
    def update_equipment(
        equipment_id: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an equipment item's details.

        Args:
            equipment_id: The UUID of the equipment to update (look up via
                `get_equipment_by_slug` if you only have the slug)
            name: New name for the equipment

        Returns:
            Dict[str, Any]: The updated equipment details
        """
        try:
            logger.info({"message": "Updating equipment", "equipment_id": equipment_id})

            updates: Dict[str, Any] = {}
            if name is not None:
                updates["name"] = name

            if not updates:
                raise ValueError("At least one field must be provided to update")

            return mealie.update_equipment(equipment_id, updates)
        except Exception as e:
            error_msg = f"Error updating equipment '{equipment_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug({"message": "Error traceback", "traceback": traceback.format_exc()})
            raise ToolError(error_msg)

    @mcp.tool()
    def delete_equipment(equipment_id: str) -> Dict[str, Any]:
        """Delete a specific equipment item.

        Args:
            equipment_id: The UUID of the equipment to delete (look up via
                `get_equipment_by_slug` if you only have the slug)

        Returns:
            Dict[str, Any]: Confirmation of deletion
        """
        try:
            logger.info({"message": "Deleting equipment", "equipment_id": equipment_id})
            return mealie.delete_equipment(equipment_id)
        except Exception as e:
            error_msg = f"Error deleting equipment '{equipment_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug({"message": "Error traceback", "traceback": traceback.format_exc()})
            raise ToolError(error_msg)
