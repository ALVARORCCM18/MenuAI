"use client";

import { useEffect, useState } from "react";
import { AiReasoningCard } from "@/components/AiReasoningCard";
import { ContextSimulator } from "@/components/ContextSimulator";
import { DishCard } from "@/components/DishCard";
import { getMenu } from "@/lib/api";
import type { MenuResponse } from "@/types";

const initialWeather = "Soleado";
const initialTime = "Tarde";

export default function MenuPage() {
  const [menuData, setMenuData] = useState<MenuResponse | null>(null);
  const [weather, setWeather] = useState(initialWeather);
  const [time, setTime] = useState(initialTime);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadMenu(selectedWeather = weather, selectedTime = time) {
    setIsLoading(true);
    setError(null);

    try {
      const result = await getMenu(selectedWeather, selectedTime);
      setMenuData(result);
    } catch (err) {
      setError("No se pudo cargar el menú. Verifica que el backend esté activo.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadMenu(initialWeather, initialTime);
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Menu Cliente</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-900">Menú recomendado</h1>
          <p className="mt-2 text-slate-600">
            El sistema prioriza platos según stock, margen y contexto de clima/hora.
          </p>
        </div>
        <ContextSimulator
          weather={weather}
          time={time}
          onContextChange={(next) => {
            setWeather(next.weather);
            setTime(next.time);
            loadMenu(next.weather, next.time);
          }}
          buttonLabel="Actualizar menú"
        />
      </section>

      {isLoading && (
        <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center text-slate-700 shadow-card">
          Cargando menú inteligente...
        </div>
      )}

      {error && (
        <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-rose-700 shadow-card">
          {error}
        </div>
      )}

      {menuData && (
        <>
          <AiReasoningCard aiReasoning={menuData.ai_reasoning} />
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {menuData.menu.map((dish, index) => (
              <DishCard key={dish.id} dish={dish} rank={index + 1} />
            ))}
          </div>
        </>
      )}
    </main>
  );
}
