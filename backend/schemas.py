from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, conint


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
