"use client";

import { useEffect, useState } from "react";
import { AiReasoningCard } from "@/components/AiReasoningCard";
import { ContextSimulator } from "@/components/ContextSimulator";
import { InventoryRow } from "@/components/InventoryRow";
import { fetchInventory, fetchMenu, updateInventoryStock } from "@/lib/api";
import type { Product, MenuResponse } from "@/types";

const defaultWeather = "Soleado";
const defaultTime = "Tarde";

export default function AdminPage() {
  const [inventory, setInventory] = useState<Product[]>([]);
  const [weather, setWeather] = useState(defaultWeather);
  const [time, setTime] = useState(defaultTime);
  const [aiReasoning, setAiReasoning] = useState<string | null>(null);
  const [loadingInventory, setLoadingInventory] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadInventory() {
    setLoadingInventory(true);
    setError(null);

    try {
      const inventoryData = await fetchInventory();
      setInventory(inventoryData);
    } catch (err) {
      setError("No se pudo cargar el inventario. Verifica el backend.");
    } finally {
      setLoadingInventory(false);
    }
  }

  async function loadAiReasoning(selectedWeather = weather, selectedTime = time) {
    setLoadingAI(true);
    setError(null);

    try {
      const result: MenuResponse = await fetchMenu(selectedWeather, selectedTime);
      setAiReasoning(result.ai_reasoning);
    } catch (err) {
      setError("No se pudo generar la estrategia de IA.");
    } finally {
      setLoadingAI(false);
    }
  }

  useEffect(() => {
    loadInventory();
    loadAiReasoning();
  }, []);

  async function handleStockChange(productId: number, stockLevel: number) {
    setError(null);
    try {
      await updateInventoryStock(productId, stockLevel);
      await loadInventory();
    } catch (err) {
      setError("No se pudo actualizar el stock. Intenta nuevamente.");
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="mb-8 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Panel administrativo</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-900">Control de inventario y simulación</h1>
          <p className="mt-2 text-slate-600">
            Ajusta niveles de stock y evalúa la estrategia de IA según clima y hora.
          </p>
        </div>
        <ContextSimulator
          weather={weather}
          time={time}
          buttonLabel="Simular IA"
          onContextChange={(next) => {
            setWeather(next.weather);
            setTime(next.time);
            loadAiReasoning(next.weather, next.time);
          }}
        />
      </section>

      {error && (
        <div className="mb-6 rounded-3xl border border-rose-200 bg-rose-50 p-6 text-rose-700 shadow-card">
          {error}
        </div>
      )}

      <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Inventario actual</h2>
            <p className="text-sm text-slate-500">Modifica stock manualmente y la tabla se actualizará.</p>
          </div>
          {loadingInventory && <p className="text-sm text-slate-500">Actualizando inventario…</p>}
        </div>

        <div className="mt-6 space-y-4">
          {inventory.map((product) => (
            <InventoryRow key={product.id} product={product} onStockChange={handleStockChange} />
          ))}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
          <h2 className="text-xl font-semibold text-slate-900">Monitoreo del inventario</h2>
          <p className="mt-2 text-slate-500">
            Ajusta el stock y el contexto desde la izquierda para ver la reacción de la IA.
          </p>
          <div className="mt-6 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3">Producto</th>
                  <th className="px-4 py-3">Stock</th>
                  <th className="px-4 py-3">Margen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {inventory.map((product) => (
                  <tr key={product.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900">{product.name}</td>
                    <td className="px-4 py-3">{product.stock_level}</td>
                    <td className="px-4 py-3">€{product.margin.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <AiReasoningCard
          aiReasoning={aiReasoning ?? "Generando razonamiento de IA..."}
          loading={loadingAI}
        />
      </section>
    </main>
  );
}
