import os
from typing import List, Optional
import logging

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend import crud, models, openai_client
from backend.database import Base, engine, get_db
from backend.schemas import InventoryUpdate, MenuResponse, ProductResponse
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
    except SQLAlchemyError:
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
