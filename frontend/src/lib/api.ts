import type { MenuResponse, Product } from "@/types";

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
