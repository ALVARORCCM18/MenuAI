import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from backend.database import Base, engine, SessionLocal
from backend.models import Product, Ingredient, Dish, DishIngredient

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


INGREDIENTS_V2 = [
    {
        "name": "Tomate fresco",
        "description": "Tomate maduro para elaboraciones base y salsas.",
        "price_per_unit": 0.85,
        "category": "Produce",
        "stock_level": 40,
        "min_stock": 10,
        "unit_type": "kg",
        "tags": ["fresco", "vegetal"],
    },
    {
        "name": "Queso manchego",
        "description": "Queso curado para recetas calientes y frías.",
        "price_per_unit": 1.9,
        "category": "Dairy",
        "stock_level": 15,
        "min_stock": 4,
        "unit_type": "kg",
        "tags": ["lacteo", "premium"],
    },
    {
        "name": "Pan brioche",
        "description": "Pan suave para hamburguesas y sandwiches.",
        "price_per_unit": 0.65,
        "category": "Bakery",
        "stock_level": 30,
        "min_stock": 8,
        "unit_type": "pieces",
        "tags": ["pan", "suave"],
    },
    {
        "name": "Carne de ternera",
        "description": "Carne para hamburguesas premium.",
        "price_per_unit": 3.5,
        "category": "Meat",
        "stock_level": 20,
        "min_stock": 5,
        "unit_type": "kg",
        "tags": ["proteina", "premium"],
    },
    {
        "name": "Huevos frescos",
        "description": "Huevos para desayunos y tortillas.",
        "price_per_unit": 0.2,
        "category": "Dairy",
        "stock_level": 50,
        "min_stock": 10,
        "unit_type": "pieces",
        "tags": ["desayuno", "mañana"],
    },
    {
        "name": "Plátano",
        "description": "Fruta para batidos y desayunos.",
        "price_per_unit": 0.5,
        "category": "Produce",
        "stock_level": 30,
        "min_stock": 5,
        "unit_type": "pieces",
        "tags": ["fresco", "desayuno", "soleado"],
    },
    {
        "name": "Chocolate",
        "description": "Chocolate para bebidas calientes y postres.",
        "price_per_unit": 1.2,
        "category": "Grocery",
        "stock_level": 25,
        "min_stock": 5,
        "unit_type": "kg",
        "tags": ["postre", "caliente"],
    },
    {
        "name": "Leche",
        "description": "Leche fresca para bebidas calientes y cocina.",
        "price_per_unit": 0.9,
        "category": "Dairy",
        "stock_level": 40,
        "min_stock": 10,
        "unit_type": "liters",
        "tags": ["caliente", "bebe"],
    },
]


DISHES_V2 = [
    {
        "name": "Hamburguesa Premium",
        "description": "Hamburguesa con pan brioche, queso manchego y carne de ternera.",
        "price": 15.9,
        "category": "Plato Principal",
        "tags": ["gourmet", "caliente"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Pan brioche", "quantity_needed": 2},
            {"ingredient_name": "Queso manchego", "quantity_needed": 0.12},
            {"ingredient_name": "Carne de ternera", "quantity_needed": 0.18},
        ],
    },
    {
        "name": "Tosta Mediterranea",
        "description": "Tosta con tomate fresco y queso manchego.",
        "price": 9.5,
        "category": "Entrante",
        "tags": ["fresco", "vegetariano"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Pan brioche", "quantity_needed": 1},
            {"ingredient_name": "Tomate fresco", "quantity_needed": 0.08},
            {"ingredient_name": "Queso manchego", "quantity_needed": 0.05},
        ],
    },
    {
        "name": "Desayuno Energético",
        "description": "Huevos revueltos con pan y plátano.",
        "price": 7.0,
        "category": "Desayuno",
        "tags": ["desayuno", "mañana", "fresco"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Huevos frescos", "quantity_needed": 2},
            {"ingredient_name": "Pan brioche", "quantity_needed": 1},
            {"ingredient_name": "Plátano", "quantity_needed": 1},
        ],
    },
    {
        "name": "Sopa Reconfortante",
        "description": "Sopa caliente ideal para días fríos y lluviosos.",
        "price": 6.5,
        "category": "Entrante",
        "tags": ["caliente", "confort", "frio", "lluvia"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Tomate fresco", "quantity_needed": 0.2},
            {"ingredient_name": "Carne de ternera", "quantity_needed": 0.05},
        ],
    },
    {
        "name": "Smoothie Tropical",
        "description": "Batido frío y fresco para días soleados.",
        "price": 5.5,
        "category": "Bebida",
        "tags": ["fresco", "soleado", "desayuno"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Plátano", "quantity_needed": 1},
        ],
    },
    {
        "name": "Chocolate Caliente",
        "description": "Bebida caliente para noches frías.",
        "price": 3.5,
        "category": "Bebida",
        "tags": ["caliente", "noche", "postre", "frio"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Chocolate", "quantity_needed": 0.05},
            {"ingredient_name": "Leche", "quantity_needed": 0.2},
        ],
    },
    {
        "name": "Tacos Picantes",
        "description": "Tacos para cenas picantes y noches animadas.",
        "price": 11.0,
        "category": "Plato Principal",
        "tags": ["noche", "picante", "caliente"],
        "is_active": True,
        "ingredients": [
            {"ingredient_name": "Carne de ternera", "quantity_needed": 0.12},
        ],
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        existing_products = session.query(Product).count()
        if not existing_products:
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
        else:
            print(f"La base de datos ya tiene {existing_products} productos legacy. Se mantendran.")

        existing_ingredients = {item.name: item for item in session.query(Ingredient).all()}
        for item in INGREDIENTS_V2:
            if item["name"] in existing_ingredients:
                continue
            ingredient = Ingredient(**item)
            session.add(ingredient)
            session.flush()
            existing_ingredients[ingredient.name] = ingredient

        existing_dishes = {item.name for item in session.query(Dish).all()}
        for item in DISHES_V2:
            if item["name"] in existing_dishes:
                continue

            dish_ingredients = item["ingredients"]
            dish_data = {key: value for key, value in item.items() if key != "ingredients"}
            dish = Dish(**dish_data)
            session.add(dish)
            session.flush()

            for line in dish_ingredients:
                ingredient = existing_ingredients[line["ingredient_name"]]
                session.add(
                    DishIngredient(
                        dish_id=dish.id,
                        ingredient_id=ingredient.id,
                        quantity_needed=line["quantity_needed"],
                    )
                )

        session.commit()
        print("Seed completado: datos legacy y v2 agregados a la base de datos.")
    except SQLAlchemyError as error:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
