import logging
import traceback
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_units_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all unit-related tools with the MCP server.

    Units are the measurement units (e.g. "g", "tbsp", "cup") attached to
    recipe ingredients. They are referenced from recipe ingredients and
    shopping list items by UUID.
    """

    @mcp.tool()
    def get_units(
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all ingredient units with pagination.

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            search: Search term to filter units

        Returns:
            Dict[str, Any]: Units with pagination information
        """
        try:
            logger.info(
                {
                    "message": "Fetching units",
                    "page": page,
                    "per_page": per_page,
                    "search": search,
                }
            )
            return mealie.get_units(page=page, per_page=per_page, search=search)
        except Exception as e:
            error_msg = f"Error fetching units: {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def get_unit(unit_id: str) -> Dict[str, Any]:
        """Get a specific unit by UUID.

        Args:
            unit_id: The UUID of the unit

        Returns:
            Dict[str, Any]: The unit details
        """
        try:
            logger.info({"message": "Fetching unit", "unit_id": unit_id})
            return mealie.get_unit(unit_id)
        except Exception as e:
            error_msg = f"Error fetching unit '{unit_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def create_unit(
        name: str,
        abbreviation: Optional[str] = None,
        plural_name: Optional[str] = None,
        plural_abbreviation: Optional[str] = None,
        description: Optional[str] = None,
        fraction: Optional[bool] = None,
        use_abbreviation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a new ingredient unit.

        Use this when `create_recipe` or `update_recipe` reports an unknown
        unit name. Names and abbreviations are matched case-sensitively
        during ingredient resolution, so prefer matching the existing
        convention rather than creating near-duplicates.

        Args:
            name: Name of the unit (e.g. "gram", "tablespoon")
            abbreviation: Optional short form (e.g. "g", "tbsp")
            plural_name: Optional plural form (e.g. "grams")
            plural_abbreviation: Optional plural short form
            description: Optional description
            fraction: Whether quantities should display as fractions (default true)
            use_abbreviation: Whether to display the abbreviation by default

        Returns:
            Dict[str, Any]: The created unit details
        """
        try:
            logger.info({"message": "Creating unit", "name": name})
            return mealie.create_unit(
                name=name,
                abbreviation=abbreviation,
                plural_name=plural_name,
                plural_abbreviation=plural_abbreviation,
                description=description,
                fraction=fraction,
                use_abbreviation=use_abbreviation,
            )
        except Exception as e:
            error_msg = f"Error creating unit '{name}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def update_unit(
        unit_id: str,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        plural_name: Optional[str] = None,
        plural_abbreviation: Optional[str] = None,
        description: Optional[str] = None,
        fraction: Optional[bool] = None,
        use_abbreviation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update a unit's details.

        Mealie uses PUT (full replacement) for units, so this tool fetches
        the existing unit first and merges the provided fields to avoid
        wiping unspecified values.

        Args:
            unit_id: The UUID of the unit to update
            name: New name for the unit
            abbreviation: New abbreviation
            plural_name: New plural form
            plural_abbreviation: New plural abbreviation
            description: New description
            fraction: Whether quantities display as fractions
            use_abbreviation: Whether to display the abbreviation by default

        Returns:
            Dict[str, Any]: The updated unit details
        """
        try:
            logger.info({"message": "Updating unit", "unit_id": unit_id})

            updates: Dict[str, Any] = {}
            if name is not None:
                updates["name"] = name
            if abbreviation is not None:
                updates["abbreviation"] = abbreviation
            if plural_name is not None:
                updates["pluralName"] = plural_name
            if plural_abbreviation is not None:
                updates["pluralAbbreviation"] = plural_abbreviation
            if description is not None:
                updates["description"] = description
            if fraction is not None:
                updates["fraction"] = fraction
            if use_abbreviation is not None:
                updates["useAbbreviation"] = use_abbreviation

            if not updates:
                raise ValueError("At least one field must be provided to update")

            existing = mealie.get_unit(unit_id)
            merged = {**existing, **updates}
            return mealie.update_unit(unit_id, merged)
        except Exception as e:
            error_msg = f"Error updating unit '{unit_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)

    @mcp.tool()
    def delete_unit(unit_id: str) -> Dict[str, Any]:
        """Delete a specific unit.

        Args:
            unit_id: The UUID of the unit to delete

        Returns:
            Dict[str, Any]: Confirmation of deletion
        """
        try:
            logger.info({"message": "Deleting unit", "unit_id": unit_id})
            return mealie.delete_unit(unit_id)
        except Exception as e:
            error_msg = f"Error deleting unit '{unit_id}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            raise ToolError(error_msg)
