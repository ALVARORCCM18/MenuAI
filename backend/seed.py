import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from backend.database import Base, engine, SessionLocal
from backend.models import Product

load_dotenv()


MENU_PRODUCTS = [
    {
        "name": "Sopa de Tomate Artesanal",
        "description": "Caliente, reconfortante y preparada con tomates frescos del día.",
        "price": 7.5,
        "cost": 2.5,
        "stock_level": 18,
        "category": "Entrante",
        "tags": ["caliente", "fresco"],
    },
    {
        "name": "Ensalada César Vegana",
        "description": "Lechugas mixtas, garbanzos crujientes y aderezo ligero sin ingredientes animales.",
        "price": 10.0,
        "cost": 3.25,
        "stock_level": 22,
        "category": "Ensalada",
        "tags": ["vegano", "fresco"],
    },
    {
        "name": "Bowl de Quinoa y Aguacate",
        "description": "Texto nutritivo con quinoa, verduras de temporada y aderezo cítrico.",
        "price": 12.0,
        "cost": 4.5,
        "stock_level": 12,
        "category": "Plato Principal",
        "tags": ["fresco", "vegano", "saludable"],
    },
    {
        "name": "Hamburguesa de Ternera Premium",
        "description": "Carne de alta calidad con queso manchego, cebolla caramelizada y pan brioche.",
        "price": 15.0,
        "cost": 7.0,
        "stock_level": 8,
        "category": "Plato Principal",
        "tags": ["caliente", "carne", "gourmet"],
    },
    {
        "name": "Pasta al Pesto con Piñones",
        "description": "Pasta casera con pesto fresco de albahaca y piñones tostados.",
        "price": 13.0,
        "cost": 5.0,
        "stock_level": 9,
        "category": "Pasta",
        "tags": ["fresco", "vegetariano"],
    },
    {
        "name": "Tacos de Pescado Crocantes",
        "description": "Tortillas suaves con pescado marinado, col morada y salsa cremosa de lima.",
        "price": 14.5,
        "cost": 6.0,
        "stock_level": 6,
        "category": "Mariscos",
        "tags": ["caliente", "fresco"],
    },
    {
        "name": "Risotto de Setas Silvestres",
        "description": "Arroz cremoso con setas de temporada y queso parmesano rallado.",
        "price": 14.0,
        "cost": 5.5,
        "stock_level": 14,
        "category": "Plato Principal",
        "tags": ["caliente", "vegetariano"],
    },
    {
        "name": "Ceviche de Camarón",
        "description": "Mariscos frescos en jugo de lima, cebolla morada y cilantro.",
        "price": 16.0,
        "cost": 7.25,
        "stock_level": 7,
        "category": "Mariscos",
        "tags": ["fresco", "citrico"],
    },
    {
        "name": "Pizza Margarita Crujiente",
        "description": "Tomate San Marzano, mozzarella fresca y albahaca.",
        "price": 11.0,
        "cost": 4.75,
        "stock_level": 20,
        "category": "Pizza",
        "tags": ["caliente", "clásico"],
    },
    {
        "name": "Pollo al Curry Thai",
        "description": "Pollo tierno con salsa de curry suave y arroz jazmín.",
        "price": 14.0,
        "cost": 5.75,
        "stock_level": 11,
        "category": "Plato Principal",
        "tags": ["caliente", "sabroso"],
    },
    {
        "name": "Batido Verde Energético",
        "description": "Smoothie de espinacas, plátano, manzana y jengibre.",
        "price": 6.5,
        "cost": 1.8,
        "stock_level": 30,
        "category": "Bebida",
        "tags": ["fresco", "saludable", "vegano"],
    },
    {
        "name": "Tarta de Chocolate Oscuro",
        "description": "Postre intenso con una base crujiente y mousse aterciopelada.",
        "price": 8.0,
        "cost": 2.75,
        "stock_level": 5,
        "category": "Postre",
        "tags": ["dulce", "gourmet"],
    },
    {
        "name": "Filete de Salmón a la Parrilla",
        "description": "Salmón fresco con salsa de limón y eneldo sobre verduras asadas.",
        "price": 18.0,
        "cost": 9.5,
        "stock_level": 10,
        "category": "Mariscos",
        "tags": ["caliente", "premium"],
    },
    {
        "name": "Wrap Mediterráneo de Hummus",
        "description": "Tortilla de trigo con hummus casero, verduras frescas y aceitunas.",
        "price": 9.0,
        "cost": 3.2,
        "stock_level": 17,
        "category": "Sandwich",
        "tags": ["fresco", "vegetariano"],
    },
    {
        "name": "Crema de Calabaza con Jengibre",
        "description": "Delicada crema otoñal servida con semillas tostadas.",
        "price": 7.0,
        "cost": 2.4,
        "stock_level": 13,
        "category": "Entrante",
        "tags": ["caliente", "fresco", "vegetariano"],
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        existing = session.query(Product).count()
        if existing:
            print(f"La base de datos ya tiene {existing} productos. Se omitirá la recarga completa.")
            return

        for item in MENU_PRODUCTS:
            product = Product(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                cost=item["cost"],
                stock_level=item["stock_level"],
                category=item["category"],
                tags=item["tags"],
            )
            session.add(product)

        session.commit()
        print("Seed completado: 15 platos agregados a la base de datos.")
    except SQLAlchemyError as error:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
