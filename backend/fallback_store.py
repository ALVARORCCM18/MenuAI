from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

FALLBACK_PRODUCTS: List[Dict] = [
    {"id": 1, "name": "Sopa de Tomate Artesanal", "description": "Caliente y preparada con tomates frescos.", "price": 7.5, "cost": 2.5, "margin": 5.0, "stock_level": 18, "category": "Entrante", "tags": ["caliente", "fresco"]},
    {"id": 2, "name": "Ensalada Cesar Vegana", "description": "Lechugas mixtas y aderezo vegano.", "price": 10.0, "cost": 3.25, "margin": 6.75, "stock_level": 22, "category": "Ensalada", "tags": ["vegano", "fresco"]},
    {"id": 3, "name": "Bowl de Quinoa y Aguacate", "description": "Quinoa, verduras y aderezo citrico.", "price": 12.0, "cost": 4.5, "margin": 7.5, "stock_level": 12, "category": "Plato Principal", "tags": ["fresco", "vegano"]},
    {"id": 4, "name": "Hamburguesa de Ternera Premium", "description": "Carne premium con pan brioche.", "price": 15.0, "cost": 7.0, "margin": 8.0, "stock_level": 8, "category": "Plato Principal", "tags": ["caliente", "carne"]},
    {"id": 5, "name": "Pasta al Pesto con Pinones", "description": "Pasta casera con pesto fresco.", "price": 13.0, "cost": 5.0, "margin": 8.0, "stock_level": 9, "category": "Pasta", "tags": ["fresco", "vegetariano"]},
    {"id": 6, "name": "Tacos de Pescado Crocantes", "description": "Tacos de pescado con lima.", "price": 14.5, "cost": 6.0, "margin": 8.5, "stock_level": 6, "category": "Mariscos", "tags": ["caliente", "fresco"]},
]

_state: List[Dict] = deepcopy(FALLBACK_PRODUCTS)


def list_products() -> List[Dict]:
    return deepcopy(_state)


def update_stock(product_id: int, stock_level: int) -> Optional[Dict]:
    for item in _state:
        if item["id"] == product_id:
            item["stock_level"] = stock_level
            return deepcopy(item)
    return None
