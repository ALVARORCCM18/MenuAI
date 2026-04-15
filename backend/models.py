from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    margin = Column(Float, Computed("price - cost"), nullable=False)
    stock_level = Column(Integer, nullable=False, default=0)
    category = Column(String(80), nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=[])


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    price_per_unit = Column(Numeric(12, 3), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    stock_level = Column(Numeric(12, 3), nullable=False, default=0)
    min_stock = Column(Numeric(12, 3), nullable=False, default=5)
    unit_type = Column(String(50), nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    dish_links = relationship("DishIngredient", back_populates="ingredient", cascade="all, delete-orphan")
    stock_transactions = relationship("StockTransaction", back_populates="ingredient")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    tags = Column(ARRAY(String), nullable=False, default=[])
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    ingredients = relationship("DishIngredient", back_populates="dish", cascade="all, delete-orphan")


class DishIngredient(Base):
    __tablename__ = "dish_ingredients"
    __table_args__ = (UniqueConstraint("dish_id", "ingredient_id", name="uq_dish_ingredient"),)

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_needed = Column(Numeric(12, 3), nullable=False)

    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dish_links")


class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False)
    quantity_changed = Column(Numeric(12, 3), nullable=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    ingredient = relationship("Ingredient", back_populates="stock_transactions")
