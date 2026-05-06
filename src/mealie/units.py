import logging
from typing import Any, Dict, Optional

from utils import format_api_params

logger = logging.getLogger("mealie-mcp")


class UnitsMixin:
    """Mixin class for ingredient unit API endpoints.

    Units are the measurement units (e.g. "g", "tbsp", "cup") attached to
    recipe ingredients. They live at `/api/units` and are referenced from
    recipe ingredients and shopping list items by UUID.
    """

    def get_units(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        search: Optional[str] = None,
        query_filter: Optional[str] = None,
        order_by_null_position: Optional[str] = None,
        pagination_seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all ingredient units.

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            order_by: Field to order results by
            order_direction: Direction to order results ('asc' or 'desc')
            search: Search term to filter units
            query_filter: Advanced query filter
            order_by_null_position: How to handle nulls in ordering ('first' or 'last')
            pagination_seed: Seed for consistent pagination

        Returns:
            JSON response containing unit items and pagination information
        """
        param_dict = {
            "page": page,
            "perPage": per_page,
            "orderBy": order_by,
            "orderDirection": order_direction,
            "search": search,
            "queryFilter": query_filter,
            "orderByNullPosition": order_by_null_position,
            "paginationSeed": pagination_seed,
        }

        params = format_api_params(param_dict)

        logger.info({"message": "Retrieving units", "parameters": params})
        return self._handle_request("GET", "/api/units", params=params)

    def get_unit(self, unit_id: str) -> Dict[str, Any]:
        """Get a specific unit by UUID.

        Args:
            unit_id: The UUID of the unit

        Returns:
            JSON response containing the unit details
        """
        if not unit_id:
            raise ValueError("Unit ID cannot be empty")

        logger.info({"message": "Retrieving unit", "unit_id": unit_id})
        return self._handle_request("GET", f"/api/units/{unit_id}")

    def create_unit(
        self,
        name: str,
        abbreviation: Optional[str] = None,
        plural_name: Optional[str] = None,
        plural_abbreviation: Optional[str] = None,
        description: Optional[str] = None,
        fraction: Optional[bool] = None,
        use_abbreviation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a new ingredient unit.

        Args:
            name: Name of the unit (e.g. "gram", "tablespoon")
            abbreviation: Optional short form (e.g. "g", "tbsp")
            plural_name: Optional plural form (e.g. "grams")
            plural_abbreviation: Optional plural short form
            description: Optional description
            fraction: Whether quantities should be displayed as fractions (default true)
            use_abbreviation: Whether to display the abbreviation by default

        Returns:
            JSON response containing the created unit
        """
        if not name:
            raise ValueError("Unit name cannot be empty")

        payload: Dict[str, Any] = {"name": name}
        if abbreviation is not None:
            payload["abbreviation"] = abbreviation
        if plural_name is not None:
            payload["pluralName"] = plural_name
        if plural_abbreviation is not None:
            payload["pluralAbbreviation"] = plural_abbreviation
        if description is not None:
            payload["description"] = description
        if fraction is not None:
            payload["fraction"] = fraction
        if use_abbreviation is not None:
            payload["useAbbreviation"] = use_abbreviation

        logger.info({"message": "Creating unit", "name": name})
        return self._handle_request("POST", "/api/units", json=payload)

    def update_unit(self, unit_id: str, unit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific unit.

        Args:
            unit_id: The UUID of the unit to update
            unit_data: Dictionary containing the unit properties to update

        Returns:
            JSON response containing the updated unit
        """
        if not unit_id:
            raise ValueError("Unit ID cannot be empty")
        if not unit_data:
            raise ValueError("Unit data cannot be empty")

        logger.info({"message": "Updating unit", "unit_id": unit_id})
        return self._handle_request(
            "PUT", f"/api/units/{unit_id}", json=unit_data
        )

    def delete_unit(self, unit_id: str) -> Dict[str, Any]:
        """Delete a specific unit.

        Args:
            unit_id: The UUID of the unit to delete

        Returns:
            JSON response confirming deletion
        """
        if not unit_id:
            raise ValueError("Unit ID cannot be empty")

        logger.info({"message": "Deleting unit", "unit_id": unit_id})
        return self._handle_request("DELETE", f"/api/units/{unit_id}")
