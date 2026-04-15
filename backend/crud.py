from decimal import Decimal
from typing import Dict, Iterable, List, Optional
from sqlalchemy import Select, select, update
from sqlalchemy.orm import Session, joinedload
from backend import models


def get_all_products(db: Session) -> List[models.Product]:
    statement = select(models.Product).order_by(models.Product.id)
    return db.execute(statement).scalars().all()


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    statement = select(models.Product).where(models.Product.id == product_id)
    return db.execute(statement).scalar_one_or_none()


def update_product_stock(db: Session, product_id: int, new_stock_level: int) -> Optional[models.Product]:
    statement = (
        update(models.Product)
        .where(models.Product.id == product_id)
        .values(stock_level=new_stock_level)
        .execution_options(synchronize_session="fetch")
        .returning(models.Product)
    )
    result = db.execute(statement)
    db.commit()
    return result.scalar_one_or_none()


def order_products_by_ids(
    products: Iterable[models.Product], priority_ids: List[int]
) -> List[models.Product]:
    product_map: Dict[int, models.Product] = {product.id: product for product in products}
    ordered: List[models.Product] = []

    for product_id in priority_ids:
        item = product_map.pop(product_id, None)
        if item is not None:
            ordered.append(item)

    remaining = sorted(product_map.values(), key=lambda item: item.margin, reverse=True)
    ordered.extend(remaining)
    return ordered


def get_all_ingredients(db: Session) -> List[models.Ingredient]:
    statement = select(models.Ingredient).order_by(models.Ingredient.name)
    return db.execute(statement).scalars().all()


def get_ingredient_by_id(db: Session, ingredient_id: int) -> Optional[models.Ingredient]:
    statement = select(models.Ingredient).where(models.Ingredient.id == ingredient_id)
    return db.execute(statement).scalar_one_or_none()


def create_ingredient(db: Session, payload: dict) -> models.Ingredient:
    ingredient = models.Ingredient(**payload)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def update_ingredient_stock(
    db: Session, ingredient_id: int, new_stock_level: Decimal
) -> Optional[models.Ingredient]:
    statement = (
        update(models.Ingredient)
        .where(models.Ingredient.id == ingredient_id)
        .values(stock_level=new_stock_level)
        .execution_options(synchronize_session="fetch")
        .returning(models.Ingredient)
    )
    result = db.execute(statement)
    db.commit()
    return result.scalar_one_or_none()


def _dish_query() -> Select[tuple[models.Dish]]:
    return (
        select(models.Dish)
        .options(
            joinedload(models.Dish.ingredients).joinedload(models.DishIngredient.ingredient),
        )
        .order_by(models.Dish.id)
    )


def get_all_dishes(db: Session, active_only: bool = True) -> List[models.Dish]:
    statement = _dish_query()
    if active_only:
        statement = statement.where(models.Dish.is_active.is_(True))
    return db.execute(statement).unique().scalars().all()


def get_dish_by_id(db: Session, dish_id: int) -> Optional[models.Dish]:
    statement = _dish_query().where(models.Dish.id == dish_id)
    return db.execute(statement).unique().scalar_one_or_none()


def create_dish_with_ingredients(db: Session, payload: dict) -> models.Dish:
    ingredients_payload = payload.pop("ingredients", [])
    dish = models.Dish(**payload)
    db.add(dish)
    db.flush()

    for item in ingredients_payload:
        link = models.DishIngredient(
            dish_id=dish.id,
            ingredient_id=item["ingredient_id"],
            quantity_needed=item["quantity_needed"],
        )
        db.add(link)

    db.commit()
    return get_dish_by_id(db, dish.id)  # type: ignore[return-value]


def compute_dish_cost(dish: models.Dish) -> Decimal:
    total = Decimal("0")
    for link in dish.ingredients:
        total += Decimal(link.quantity_needed) * Decimal(link.ingredient.price_per_unit)
    return total


def compute_dish_available_servings(dish: models.Dish) -> int:
    if not dish.ingredients:
        return 0

    max_by_ingredient: List[int] = []
    for link in dish.ingredients:
        needed = Decimal(link.quantity_needed)
        if needed <= 0:
            return 0
        servings = int(Decimal(link.ingredient.stock_level) // needed)
        max_by_ingredient.append(servings)
    return min(max_by_ingredient) if max_by_ingredient else 0


def sell_dish_atomic(
    db: Session,
    dish_id: int,
    quantity: int,
    created_by: Optional[str] = None,
    notes: Optional[str] = None,
) -> tuple[models.Dish, List[models.DishIngredient]]:
    dish = get_dish_by_id(db, dish_id)
    if not dish:
        raise ValueError("DISH_NOT_FOUND")
    if not dish.ingredients:
        raise ValueError("DISH_WITHOUT_INGREDIENTS")

    ingredient_ids = [item.ingredient_id for item in dish.ingredients]
    lock_statement = (
        select(models.Ingredient)
        .where(models.Ingredient.id.in_(ingredient_ids))
        .with_for_update()
    )
    locked_ingredients = db.execute(lock_statement).scalars().all()
    by_id = {item.id: item for item in locked_ingredients}

    for link in dish.ingredients:
        ingredient = by_id.get(link.ingredient_id)
        if ingredient is None:
            raise ValueError("INGREDIENT_NOT_FOUND")

        required = Decimal(link.quantity_needed) * Decimal(quantity)
        if Decimal(ingredient.stock_level) < required:
            raise ValueError("INSUFFICIENT_STOCK")

    for link in dish.ingredients:
        ingredient = by_id[link.ingredient_id]
        required = Decimal(link.quantity_needed) * Decimal(quantity)
        ingredient.stock_level = Decimal(ingredient.stock_level) - required
        db.add(
            models.StockTransaction(
                ingredient_id=ingredient.id,
                transaction_type="SOLD",
                quantity_changed=-required,
                reference_type="DISH_SALE",
                reference_id=dish.id,
                notes=notes,
                created_by=created_by,
            )
        )

    db.commit()
    updated_dish = get_dish_by_id(db, dish.id)
    if not updated_dish:
        raise ValueError("DISH_NOT_FOUND")
    return updated_dish, updated_dish.ingredients


def get_recent_stock_transactions(
    db: Session, ingredient_id: Optional[int] = None, limit: int = 100
) -> List[models.StockTransaction]:
    statement = select(models.StockTransaction).order_by(models.StockTransaction.created_at.desc())
    if ingredient_id is not None:
        statement = statement.where(models.StockTransaction.ingredient_id == ingredient_id)
    statement = statement.limit(limit)
    return db.execute(statement).scalars().all()
