import type {
  CreateDishPayload,
  DishSaleResult,
  DishV2,
  Ingredient,
  MenuResponse,
  Product,
  SellDishPayload,
  StockTransaction,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Error en la solicitud al backend.");
  }
  return response.json();
}

export async function getMenu(weather?: string, time?: string): Promise<MenuResponse> {
  const params = new URLSearchParams();
  if (weather) params.set("weather", weather);
  if (time) params.set("time", time);

  const response = await fetch(`${BASE_URL}/menu?${params.toString()}`);
  return handleResponse<MenuResponse>(response);
}

export const fetchMenu = getMenu;

export async function fetchInventory(): Promise<Product[]> {
  const response = await fetch(`${BASE_URL}/admin/inventory`);
  return handleResponse<Product[]>(response);
}

export async function updateInventoryStock(productId: number, stockLevel: number): Promise<Product> {
  const response = await fetch(`${BASE_URL}/admin/inventory/${productId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stock_level: stockLevel }),
  });
  return handleResponse<Product>(response);
}

export async function getIngredients(): Promise<Ingredient[]> {
  const response = await fetch(`${BASE_URL}/v2/ingredients`);
  return handleResponse<Ingredient[]>(response);
}

export async function createIngredient(payload: Omit<Ingredient, "id">): Promise<Ingredient> {
  const response = await fetch(`${BASE_URL}/v2/ingredients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<Ingredient>(response);
}

export async function updateIngredientStock(ingredientId: number, stockLevel: number): Promise<Ingredient> {
  const response = await fetch(`${BASE_URL}/v2/ingredients/${ingredientId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stock_level: stockLevel }),
  });
  return handleResponse<Ingredient>(response);
}

export async function getDishesV2(includeInactive = false): Promise<DishV2[]> {
  const params = new URLSearchParams();
  if (includeInactive) params.set("include_inactive", "true");
  const query = params.toString();
  const endpoint = query ? `/v2/dishes?${query}` : "/v2/dishes";
  const response = await fetch(`${BASE_URL}${endpoint}`);
  return handleResponse<DishV2[]>(response);
}

export async function createDishV2(payload: CreateDishPayload): Promise<DishV2> {
  const response = await fetch(`${BASE_URL}/v2/dishes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<DishV2>(response);
}

export async function sellDishV2(payload: SellDishPayload): Promise<DishSaleResult> {
  const response = await fetch(`${BASE_URL}/v2/sales`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<DishSaleResult>(response);
}

export async function getStockTransactions(
  ingredientId?: number,
  limit = 100,
): Promise<StockTransaction[]> {
  const params = new URLSearchParams();
  if (ingredientId) params.set("ingredient_id", ingredientId.toString());
  params.set("limit", limit.toString());
  const response = await fetch(`${BASE_URL}/v2/stock-transactions?${params.toString()}`);
  return handleResponse<StockTransaction[]>(response);
}
