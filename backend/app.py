import os
from decimal import Decimal
from typing import List, Optional
import logging

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend import crud, models, openai_client
from backend.database import Base, engine, get_db
from backend.schemas import (
    DishCreate,
    DishIngredientResponse,
    DishResponse,
    DishSaleRequest,
    DishSaleResponse,
    IngredientCreate,
    IngredientResponse,
    IngredientStockUpdate,
    InventoryUpdate,
    MenuResponse,
    ProductResponse,
    StockTransactionResponse,
)
from backend import fallback_store


app = FastAPI(
    title="MenuIA Backend",
    description="API para recomendaciones dinámicas de menú basadas en inventario, margen y contexto.",
)

logger = logging.getLogger(__name__)

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    auto_create_schema = os.getenv("AUTO_CREATE_SCHEMA", "false").lower() == "true"
    if not auto_create_schema:
        logger.info("AUTO_CREATE_SCHEMA=false: se omite create_all y se espera migracion Alembic.")
        return

    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        # Keep the API alive so /docs is available even when DB is down.
        logger.warning("No se pudo inicializar la base de datos al arrancar: %s", exc)


@app.get("/menu", response_model=MenuResponse)
def get_menu(
    weather: Optional[str] = Query(None, description="Clima actual"),
    time: Optional[str] = Query(None, description="Franja horaria"),
    db: Session = Depends(get_db),
) -> MenuResponse:
    try:
        # Prefer v2 dishes as source of truth so admin changes affect the client menu.
        dishes = crud.get_all_dishes(db, active_only=True)
        if not dishes:
            # Fallback to legacy products if no v2 dishes exist.
            products = crud.get_all_products(db)
            if not products:
                raise HTTPException(status_code=404, detail="No hay productos en el inventario.")

            product_dicts = [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "price": item.price,
                    "cost": item.cost,
                    "margin": item.margin,
                    "stock_level": item.stock_level,
                    "category": item.category,
                    "tags": item.tags,
                }
                for item in products
            ]
            ai_recommendation = openai_client.rank_menu(product_dicts, weather=weather, time_of_day=time)
            ordered_products = crud.order_products_by_ids(products, ai_recommendation.recommended_ids)

            return MenuResponse(
                recommended_ids=ai_recommendation.recommended_ids,
                ai_reasoning=ai_recommendation.ai_reasoning,
                menu=[ProductResponse.from_orm(product) for product in ordered_products],
            )

        # Build product-like dicts from dishes so the ranking can consume the same schema.
        dish_dicts = []
        dish_map = {}
        for d in dishes:
            cost = crud.compute_dish_cost(d)
            margin = float(Decimal(d.price) - cost)
            available = crud.compute_dish_available_servings(d)
            entry = {
                "id": d.id,
                "name": d.name,
                "description": d.description or "",
                "price": float(d.price),
                "cost": float(cost),
                "margin": float(margin),
                "stock_level": int(available),
                "category": d.category,
                "tags": d.tags,
            }
            dish_dicts.append(entry)
            dish_map[d.id] = entry

        ai_recommendation = openai_client.rank_menu(dish_dicts, weather=weather, time_of_day=time)

        # Order dishes according to recommended ids, then by margin desc for remaining.
        ordered: list[dict] = []
        remaining = {d["id"]: d for d in dish_dicts}
        for pid in ai_recommendation.recommended_ids:
            item = remaining.pop(pid, None)
            if item:
                ordered.append(item)

        if remaining:
            rest_sorted = sorted(remaining.values(), key=lambda it: it.get("margin", 0), reverse=True)
            ordered.extend(rest_sorted)

        return MenuResponse(
            recommended_ids=ai_recommendation.recommended_ids,
            ai_reasoning=ai_recommendation.ai_reasoning,
            menu=[ProductResponse.model_validate(product) for product in ordered],
        )
    except SQLAlchemyError:
        # Keep previous fallback behavior when DB errors occur.
        fallback_products = fallback_store.list_products()
        ai_recommendation = openai_client.rank_menu(fallback_products, weather=weather, time_of_day=time)
        priority = {item_id: idx for idx, item_id in enumerate(ai_recommendation.recommended_ids)}
        ordered = sorted(
            fallback_products,
            key=lambda item: priority.get(item["id"], 10_000),
        )
        return MenuResponse(
            recommended_ids=ai_recommendation.recommended_ids,
            ai_reasoning=ai_recommendation.ai_reasoning,
            menu=[ProductResponse.model_validate(product) for product in ordered],
        )


@app.get("/admin/inventory", response_model=List[ProductResponse])
def get_inventory(db: Session = Depends(get_db)) -> List[ProductResponse]:
    try:
        products = crud.get_all_products(db)
        return [ProductResponse.from_orm(product) for product in products]
    except SQLAlchemyError:
        return [ProductResponse.model_validate(product) for product in fallback_store.list_products()]


@app.patch("/admin/inventory/{product_id}", response_model=ProductResponse)
def patch_inventory(
    product_id: int,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    try:
        product = crud.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        updated = crud.update_product_stock(db, product_id, inventory_update.stock_level)
        if not updated:
            raise HTTPException(status_code=500, detail="No se pudo actualizar el stock.")

        return ProductResponse.from_orm(updated)
    except SQLAlchemyError:
        updated = fallback_store.update_stock(product_id, inventory_update.stock_level)
        if not updated:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        return ProductResponse.model_validate(updated)


def _build_dish_response(dish: models.Dish) -> DishResponse:
    ingredients = [
        DishIngredientResponse(
            ingredient_id=link.ingredient_id,
            ingredient_name=link.ingredient.name,
            unit_type=link.ingredient.unit_type,
            quantity_needed=Decimal(link.quantity_needed),
            current_stock_level=Decimal(link.ingredient.stock_level),
        )
        for link in dish.ingredients
    ]
    cost = crud.compute_dish_cost(dish)
    margin = Decimal(dish.price) - cost
    return DishResponse(
        id=dish.id,
        name=dish.name,
        description=dish.description,
        price=Decimal(dish.price),
        category=dish.category,
        tags=dish.tags,
        is_active=dish.is_active,
        cost=cost,
        margin=margin,
        available_servings=crud.compute_dish_available_servings(dish),
        ingredients=ingredients,
    )


@app.get("/v2/ingredients", response_model=List[IngredientResponse])
def get_ingredients_v2(db: Session = Depends(get_db)) -> List[IngredientResponse]:
    ingredients = crud.get_all_ingredients(db)
    return [IngredientResponse.from_orm(item) for item in ingredients]


@app.post("/v2/ingredients", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient_v2(payload: IngredientCreate, db: Session = Depends(get_db)) -> IngredientResponse:
    ingredient = crud.create_ingredient(db, payload.model_dump())
    return IngredientResponse.from_orm(ingredient)


@app.patch("/v2/ingredients/{ingredient_id}", response_model=IngredientResponse)
def patch_ingredient_stock_v2(
    ingredient_id: int,
    payload: IngredientStockUpdate,
    db: Session = Depends(get_db),
) -> IngredientResponse:
    existing = crud.get_ingredient_by_id(db, ingredient_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado.")

    updated = crud.update_ingredient_stock(db, ingredient_id, payload.stock_level)
    if not updated:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el stock del ingrediente.")
    return IngredientResponse.from_orm(updated)


@app.get("/v2/dishes", response_model=List[DishResponse])
def get_dishes_v2(
    include_inactive: bool = Query(False, description="Incluir platos inactivos"),
    db: Session = Depends(get_db),
) -> List[DishResponse]:
    dishes = crud.get_all_dishes(db, active_only=not include_inactive)
    return [_build_dish_response(dish) for dish in dishes]


@app.post("/v2/dishes", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish_v2(payload: DishCreate, db: Session = Depends(get_db)) -> DishResponse:
    if not payload.ingredients:
        raise HTTPException(status_code=400, detail="Un plato debe tener al menos un ingrediente.")

    missing_ingredient_ids = [
        item.ingredient_id
        for item in payload.ingredients
        if crud.get_ingredient_by_id(db, item.ingredient_id) is None
    ]
    if missing_ingredient_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Ingredientes no encontrados: {missing_ingredient_ids}",
        )

    dish = crud.create_dish_with_ingredients(db, payload.model_dump())
    return _build_dish_response(dish)


@app.post("/v2/sales", response_model=DishSaleResponse)
def sell_dish_v2(payload: DishSaleRequest, db: Session = Depends(get_db)) -> DishSaleResponse:
    try:
        dish, consumed = crud.sell_dish_atomic(
            db,
            dish_id=payload.dish_id,
            quantity=payload.quantity,
            created_by=payload.created_by,
            notes=payload.notes,
        )
    except ValueError as exc:
        db.rollback()
        mapping = {
            "DISH_NOT_FOUND": (404, "Plato no encontrado."),
            "DISH_WITHOUT_INGREDIENTS": (400, "El plato no tiene ingredientes configurados."),
            "INGREDIENT_NOT_FOUND": (400, "La receta contiene ingredientes inexistentes."),
            "INSUFFICIENT_STOCK": (409, "Stock insuficiente para completar la venta."),
        }
        status_code, detail = mapping.get(str(exc), (400, "No se pudo completar la venta."))
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error de base de datos en la venta.") from exc

    ingredients_consumed = [
        DishIngredientResponse(
            ingredient_id=link.ingredient_id,
            ingredient_name=link.ingredient.name,
            unit_type=link.ingredient.unit_type,
            quantity_needed=Decimal(link.quantity_needed) * Decimal(payload.quantity),
            current_stock_level=Decimal(link.ingredient.stock_level),
        )
        for link in consumed
    ]
    return DishSaleResponse(
        dish_id=dish.id,
        quantity_sold=payload.quantity,
        ingredients_consumed=ingredients_consumed,
        remaining_available_servings=crud.compute_dish_available_servings(dish),
    )


@app.get("/v2/stock-transactions", response_model=List[StockTransactionResponse])
def get_stock_transactions_v2(
    ingredient_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> List[StockTransactionResponse]:
    transactions = crud.get_recent_stock_transactions(db, ingredient_id=ingredient_id, limit=limit)
    return [StockTransactionResponse.from_orm(item) for item in transactions]
