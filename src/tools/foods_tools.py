import logging
import traceback
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_foods_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all food-related tools with the MCP server.

    Foods are the named ingredients (e.g. "ground pork", "onion") that the
    recipe scaler multiplies. They are referenced from recipe ingredients
    and shopping list items by UUID.
    """

    @mcp.tool()
    def get_foods(
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all ingredient foods with pagination.

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            search: Search term to filter foods

        Returns:
            Dict[str, Any]: Foods with pagination information
        """
        try:
            logger.info(
                {
                    "message": "Fetching foods",
                    "page": page,
                    "per_page": per_page,
                    "search": search,
                }
            )
            return mealie.get_foods(page=page, per_page=per_page, search=search)
        except Exception as e:
            error_msg = f"Error fetching foods: {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def get_food(food_id: str) -> Dict[str, Any]:
        """Get a specific food by UUID.

        Args:
            food_id: The UUID of the food

        Returns:
            Dict[str, Any]: The food details
        """
        try:
            logger.info({"message": "Fetching food", "food_id": food_id})
            return mealie.get_food(food_id)
        except Exception as e:
            error_msg = f"Error fetching food '{food_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def create_food(
        name: str,
        plural_name: Optional[str] = None,
        description: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new ingredient food.

        Use this when `create_recipe` or `update_recipe` reports an unknown
        food name. Names are case-sensitive in Mealie's deduplication, so
        prefer matching the existing convention (e.g. lowercase singular)
        rather than creating near-duplicates.

        Args:
            name: Name of the food (e.g. "ground pork", "onion")
            plural_name: Optional plural form (e.g. "onions")
            description: Optional description
            label_id: Optional UUID of a multi-purpose label to associate

        Returns:
            Dict[str, Any]: The created food details
        """
        try:
            logger.info({"message": "Creating food", "name": name})
            return mealie.create_food(
                name=name,
                plural_name=plural_name,
                description=description,
                label_id=label_id,
            )
        except Exception as e:
            error_msg = f"Error creating food '{name}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def update_food(
        food_id: str,
        name: Optional[str] = None,
        plural_name: Optional[str] = None,
        description: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a food's details.

        Mealie uses PUT (full replacement) for foods, so this tool fetches
        the existing food first and merges the provided fields to avoid
        wiping unspecified values.

        Args:
            food_id: The UUID of the food to update
            name: New name for the food
            plural_name: New plural form
            description: New description
            label_id: New label UUID (pass empty string to clear is not supported here)

        Returns:
            Dict[str, Any]: The updated food details
        """
        try:
            logger.info({"message": "Updating food", "food_id": food_id})

            updates: Dict[str, Any] = {}
            if name is not None:
                updates["name"] = name
            if plural_name is not None:
                updates["pluralName"] = plural_name
            if description is not None:
                updates["description"] = description
            if label_id is not None:
                updates["labelId"] = label_id

            if not updates:
                raise ValueError("At least one field must be provided to update")

            existing = mealie.get_food(food_id)
            merged = {**existing, **updates}
            return mealie.update_food(food_id, merged)
        except Exception as e:
            error_msg = f"Error updating food '{food_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def delete_food(food_id: str) -> Dict[str, Any]:
        """Delete a specific food.

        Args:
            food_id: The UUID of the food to delete

        Returns:
            Dict[str, Any]: Confirmation of deletion
        """
        try:
            logger.info({"message": "Deleting food", "food_id": food_id})
            return mealie.delete_food(food_id)
        except Exception as e:
            error_msg = f"Error deleting food '{food_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)
