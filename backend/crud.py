from typing import Dict, Iterable, List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session
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
