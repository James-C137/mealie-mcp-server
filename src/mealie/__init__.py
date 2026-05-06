from .categories import CategoriesMixin
from .client import MealieClient
from .equipment import EquipmentMixin
from .group import GroupMixin
from .mealplan import MealplanMixin
from .recipe import RecipeMixin
from .shopping_list import ShoppingListMixin
from .tags import TagsMixin
from .user import UserMixin


class MealieFetcher(
    RecipeMixin,
    CategoriesMixin,
    TagsMixin,
    EquipmentMixin,
    ShoppingListMixin,
    MealplanMixin,
    UserMixin,
    GroupMixin,
    MealieClient,
):
    pass
