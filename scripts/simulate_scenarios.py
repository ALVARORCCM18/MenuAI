#!/usr/bin/env python3
"""
Simula escenarios de ventas y reposiciones contra la API local de MenuIA.

Uso:
  python scripts/simulate_scenarios.py --base-url http://127.0.0.1:8000

El script no necesita dependencias externas (usa urllib).
"""
import argparse
import json
from urllib import request, parse


def http_request(method: str, url: str, data=None):
    headers = {"Content-Type": "application/json"}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return raw


def get(base, path, params=None):
    url = base.rstrip("/") + path
    if params:
        url = url + "?" + parse.urlencode(params)
    return http_request("GET", url)


def post(base, path, payload):
    url = base.rstrip("/") + path
    return http_request("POST", url, data=payload)


def patch(base, path, payload):
    url = base.rstrip("/") + path
    return http_request("PATCH", url, data=payload)


def print_menu(menu_resp):
    print("\n--- MENU ---")
    print("AI reasoning:", menu_resp.get("ai_reasoning"))
    for idx, item in enumerate(menu_resp.get("menu", []), start=1):
        print(f"#{idx}: {item['name']} (id={item['id']}) stock_level={item.get('stock_level')} margin={item.get('margin')}")


def print_dishes(dishes):
    print("\n--- DISHES V2 ---")
    for d in dishes:
        print(f"id={d['id']} name={d['name']} available_servings={d.get('available_servings')} margin={d.get('margin')}")
        for ing in d.get("ingredients", []):
            print(f"   - ing id={ing['ingredient_id']} name={ing['ingredient_name']} qty_needed={ing['quantity_needed']} current_stock={ing['current_stock_level']}")


def scenario_sell_and_restock(base):
    # initial state
    menu0 = get(base, "/menu")
    dishes0 = get(base, "/v2/dishes")
    print_menu(menu0)
    print_dishes(dishes0)

    if not dishes0:
        print("No dishes available to simulate.")
        return

    first = dishes0[0]
    dish_id = first["id"]
    print(f"\nSimulamos venta de 1 unidad del plato id={dish_id} ({first['name']})")
    sale = post(base, "/v2/sales", {"dish_id": dish_id, "quantity": 1, "created_by": "simulator"})
    print("Sale response:", sale)

    menu1 = get(base, "/menu")
    dishes1 = get(base, "/v2/dishes")
    print_menu(menu1)
    print_dishes(dishes1)

    # restock the first ingredient of the first dish
    if first.get("ingredients"):
        ing = first["ingredients"][0]
        ing_id = ing["ingredient_id"]
        print(f"\nReposicionando ingrediente id={ing_id} (+10)")
        current = get(base, f"/v2/ingredients")
        found = next((x for x in current if x["id"] == ing_id), None)
        if found:
            new_level = float(found["stock_level"]) + 10
            patched = patch(base, f"/v2/ingredients/{ing_id}", {"stock_level": new_level})
            print("Patch response:", patched)
        else:
            print("Ingrediente no encontrado para reposicionar.")

    menu2 = get(base, "/menu")
    dishes2 = get(base, "/v2/dishes")
    print_menu(menu2)
    print_dishes(dishes2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url

    print("Connecting to", base)
    scenario_sell_and_restock(base)


if __name__ == "__main__":
    main()
