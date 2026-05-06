import logging
from typing import Any, Dict, Optional

from utils import format_api_params

logger = logging.getLogger("mealie-mcp")


class EquipmentMixin:
    """Mixin class for recipe equipment API endpoints.

    In Mealie, equipment is exposed under the "tools" organizer
    (`/api/organizers/tools`). We expose it as "equipment" here to avoid
    overloading the term "tool" (which already refers to MCP tools).
    """

    def get_equipment_list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all recipe equipment items with pagination.

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            order_by: Field to order results by
            order_direction: Direction to order results ('asc' or 'desc')
            search: Search term to filter equipment

        Returns:
            JSON response containing equipment items and pagination information
        """
        param_dict = {
            "page": page,
            "perPage": per_page,
            "orderBy": order_by,
            "orderDirection": order_direction,
            "search": search,
        }

        params = format_api_params(param_dict)

        logger.info({"message": "Retrieving equipment", "parameters": params})
        return self._handle_request("GET", "/api/organizers/tools", params=params)

    def get_equipment_by_slug(self, equipment_slug: str) -> Dict[str, Any]:
        """Get a specific equipment item by its slug.

        Args:
            equipment_slug: The slug of the equipment item

        Returns:
            JSON response containing the equipment details
        """
        if not equipment_slug:
            raise ValueError("Equipment slug cannot be empty")

        logger.info(
            {"message": "Retrieving equipment by slug", "equipment_slug": equipment_slug}
        )
        return self._handle_request(
            "GET", f"/api/organizers/tools/slug/{equipment_slug}"
        )
