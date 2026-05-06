"""Helpers for resolving structured recipe ingredient input into the
food/unit objects Mealie expects.

The MCP recipe tools accept ingredients as either plain strings (legacy,
free-form `note`) or structured dicts with `quantity`, `unit`, `food`,
`note`. Structured `unit`/`food` may be either an existing UUID or a name;
names are resolved against the existing food/unit vocabulary.

Resolution is intentionally fail-loud: any unknown name raises a
`ToolError` listing the unknowns instead of silently dropping to a
note-only ingredient or auto-creating duplicates. This forces the caller
into a deliberate two-step flow (attempt → see error → call
`create_food`/`create_unit` → retry) and keeps the food/unit list from
drifting over time.
"""

import logging
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple

from mcp.server.fastmcp.exceptions import ToolError

from mealie import MealieFetcher
from models.recipe import IngredientFood, IngredientUnit, RecipeIngredient

logger = logging.getLogger("mealie-mcp")

_FETCH_PAGE_SIZE = 200


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def _iter_pages(
    fetch_fn, parameters: Optional[Dict[str, Any]] = None
) -> Iterable[Dict[str, Any]]:
    """Yield every item across all pages of a paginated list endpoint."""
    page = 1
    parameters = parameters or {}
    while True:
        resp = fetch_fn(page=page, per_page=_FETCH_PAGE_SIZE, **parameters)
        items = resp.get("items", []) or []
        for item in items:
            yield item
        if len(items) < _FETCH_PAGE_SIZE:
            return
        page += 1


def _build_food_index(
    mealie: MealieFetcher,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Return (by_lower_name, by_id) lookup tables for foods.

    Names, plural names, and aliases all map to the same food. Later entries
    overwrite earlier ones, which is fine because Mealie's UI already
    discourages name collisions.
    """
    by_name: Dict[str, Dict[str, Any]] = {}
    by_id: Dict[str, Dict[str, Any]] = {}
    for food in _iter_pages(mealie.get_foods):
        if food.get("id"):
            by_id[food["id"]] = food
        for key in ("name", "pluralName"):
            value = food.get(key)
            if value:
                by_name[value.lower()] = food
        for alias in food.get("aliases") or []:
            alias_name = alias.get("name") if isinstance(alias, dict) else None
            if alias_name:
                by_name[alias_name.lower()] = food
    return by_name, by_id


def _build_unit_index(
    mealie: MealieFetcher,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Return (by_lower_name, by_id) lookup tables for units.

    Names, plural names, abbreviations, plural abbreviations, and aliases
    all map to the same unit so that `"g"`, `"gram"`, and `"grams"` resolve
    interchangeably.
    """
    by_name: Dict[str, Dict[str, Any]] = {}
    by_id: Dict[str, Dict[str, Any]] = {}
    for unit in _iter_pages(mealie.get_units):
        if unit.get("id"):
            by_id[unit["id"]] = unit
        for key in ("name", "pluralName", "abbreviation", "pluralAbbreviation"):
            value = unit.get(key)
            if value:
                by_name[value.lower()] = unit
        for alias in unit.get("aliases") or []:
            alias_name = alias.get("name") if isinstance(alias, dict) else None
            if alias_name:
                by_name[alias_name.lower()] = unit
    return by_name, by_id


def build_recipe_ingredients(
    mealie: MealieFetcher,
    ingredients: List[Any],
) -> List[RecipeIngredient]:
    """Convert mixed string/dict ingredient input into `RecipeIngredient`s.

    String items are passed through unchanged as `note`-only ingredients.
    Dict items must conform to:

        {
            "quantity": float,             # optional
            "unit":     str | None,        # name OR UUID, optional
            "food":     str | None,        # name OR UUID, optional
            "note":     str | None,        # optional
            "title":    str | None,        # optional section header
        }

    Raises `ToolError` if any food/unit name or UUID does not match an
    existing record. The error message lists every unknown so the caller
    can resolve them in a single follow-up.
    """
    string_ingredients: List[Tuple[int, str]] = []
    structured_ingredients: List[Tuple[int, Dict[str, Any]]] = []

    for index, item in enumerate(ingredients):
        if isinstance(item, str):
            string_ingredients.append((index, item))
        elif isinstance(item, dict):
            structured_ingredients.append((index, item))
        else:
            raise ToolError(
                f"Ingredient at index {index} must be a string or dict, "
                f"got {type(item).__name__}"
            )

    needs_food_lookup = any(
        isinstance(entry.get("food"), str) and entry["food"]
        for _, entry in structured_ingredients
    )
    needs_unit_lookup = any(
        isinstance(entry.get("unit"), str) and entry["unit"]
        for _, entry in structured_ingredients
    )

    foods_by_name: Dict[str, Dict[str, Any]] = {}
    foods_by_id: Dict[str, Dict[str, Any]] = {}
    units_by_name: Dict[str, Dict[str, Any]] = {}
    units_by_id: Dict[str, Dict[str, Any]] = {}

    if needs_food_lookup:
        foods_by_name, foods_by_id = _build_food_index(mealie)
    if needs_unit_lookup:
        units_by_name, units_by_id = _build_unit_index(mealie)

    unknown_foods: List[str] = []
    unknown_units: List[str] = []

    def _resolve(value: str, by_name, by_id) -> Optional[Dict[str, Any]]:
        if _is_uuid(value):
            return by_id.get(value)
        return by_name.get(value.lower())

    resolved_food: Dict[int, Optional[Dict[str, Any]]] = {}
    resolved_unit: Dict[int, Optional[Dict[str, Any]]] = {}

    for index, entry in structured_ingredients:
        food_value = entry.get("food")
        unit_value = entry.get("unit")

        if isinstance(food_value, str) and food_value:
            match = _resolve(food_value, foods_by_name, foods_by_id)
            if match is None:
                unknown_foods.append(food_value)
            resolved_food[index] = match
        else:
            resolved_food[index] = None

        if isinstance(unit_value, str) and unit_value:
            match = _resolve(unit_value, units_by_name, units_by_id)
            if match is None:
                unknown_units.append(unit_value)
            resolved_unit[index] = match
        else:
            resolved_unit[index] = None

    if unknown_foods or unknown_units:
        raise ToolError(
            f"Unknown food(s): {sorted(set(unknown_foods))}. "
            f"Unknown unit(s): {sorted(set(unknown_units))}. "
            "Use create_food / create_unit to add them, or pass an existing UUID."
        )

    result: List[Optional[RecipeIngredient]] = [None] * len(ingredients)

    for index, note in string_ingredients:
        result[index] = RecipeIngredient(note=note)

    for index, entry in structured_ingredients:
        food_obj = None
        unit_obj = None
        food_data = resolved_food.get(index)
        unit_data = resolved_unit.get(index)
        if food_data is not None:
            food_obj = IngredientFood.model_validate(food_data)
        if unit_data is not None:
            unit_obj = IngredientUnit.model_validate(unit_data)

        quantity = entry.get("quantity")
        if quantity is not None:
            try:
                quantity = float(quantity)
            except (TypeError, ValueError):
                raise ToolError(
                    f"Ingredient at index {index} has non-numeric quantity: "
                    f"{entry.get('quantity')!r}"
                )

        result[index] = RecipeIngredient(
            quantity=quantity,
            unit=unit_obj,
            food=food_obj,
            note=entry.get("note"),
            title=entry.get("title"),
            isFood=food_obj is not None,
        )

    return [r for r in result if r is not None]
