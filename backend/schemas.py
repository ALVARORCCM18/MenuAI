from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, condecimal, conint


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    cost: float
    margin: float
    stock_level: int
    category: str
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)


class InventoryUpdate(BaseModel):
    stock_level: conint(ge=0) = Field(..., description="Nuevo nivel de stock")
    model_config = ConfigDict(strict=True)


class MenuResponse(BaseModel):
    recommended_ids: List[int]
    ai_reasoning: str
    menu: List[ProductResponse]


class AIRecommendation(BaseModel):
    recommended_ids: List[int]
    ai_reasoning: str


class IngredientBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_per_unit: condecimal(ge=0, max_digits=12, decimal_places=3)
    category: str
    stock_level: condecimal(ge=0, max_digits=12, decimal_places=3) = Decimal("0")
    min_stock: condecimal(ge=0, max_digits=12, decimal_places=3) = Decimal("5")
    unit_type: str
    tags: List[str] = Field(default_factory=list)


class IngredientCreate(IngredientBase):
    pass


class IngredientStockUpdate(BaseModel):
    stock_level: condecimal(ge=0, max_digits=12, decimal_places=3)


class IngredientResponse(IngredientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DishIngredientInput(BaseModel):
    ingredient_id: int
    quantity_needed: condecimal(gt=0, max_digits=12, decimal_places=3)


class DishIngredientResponse(BaseModel):
    ingredient_id: int
    ingredient_name: str
    unit_type: str
    quantity_needed: Decimal
    current_stock_level: Decimal


class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: condecimal(ge=0, max_digits=12, decimal_places=2)
    category: str
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True
    ingredients: List[DishIngredientInput] = Field(default_factory=list)


class DishResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    category: str
    tags: List[str]
    is_active: bool
    cost: Decimal
    margin: Decimal
    available_servings: int
    ingredients: List[DishIngredientResponse]

    model_config = ConfigDict(from_attributes=True)


class DishSaleRequest(BaseModel):
    dish_id: int
    quantity: conint(gt=0) = 1
    notes: Optional[str] = None
    created_by: Optional[str] = None


class DishSaleResponse(BaseModel):
    dish_id: int
    quantity_sold: int
    ingredients_consumed: List[DishIngredientResponse]
    remaining_available_servings: int


class StockTransactionResponse(BaseModel):
    id: int
    ingredient_id: int
    transaction_type: str
    quantity_changed: Decimal
    reference_type: Optional[str]
    reference_id: Optional[int]
    notes: Optional[str]
    created_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
