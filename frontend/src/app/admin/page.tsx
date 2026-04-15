"use client";

import { useEffect, useState, type FormEvent } from "react";
import { AiReasoningCard } from "@/components/AiReasoningCard";
import { ContextSimulator } from "@/components/ContextSimulator";
import { InventoryRow } from "@/components/InventoryRow";
import {
  createDishV2,
  createIngredient,
  fetchMenu,
  getDishesV2,
  getIngredients,
  sellDishV2,
  updateIngredientStock,
} from "@/lib/api";
import type { DishV2, Ingredient, MenuResponse } from "@/types";

const defaultWeather = "Soleado";
const defaultTime = "Tarde";

type RecipeIngredientRow = {
  ingredientId: string;
  quantityNeeded: string;
};

export default function AdminPage() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [dishes, setDishes] = useState<DishV2[]>([]);
  const [weather, setWeather] = useState(defaultWeather);
  const [time, setTime] = useState(defaultTime);
  const [aiReasoning, setAiReasoning] = useState<string | null>(null);
  const [lastSaleMessage, setLastSaleMessage] = useState<string | null>(null);
  const [lastIngredientMessage, setLastIngredientMessage] = useState<string | null>(null);
  const [lastRecipeMessage, setLastRecipeMessage] = useState<string | null>(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [sellingDishId, setSellingDishId] = useState<number | null>(null);
  const [creatingIngredient, setCreatingIngredient] = useState(false);
  const [creatingRecipe, setCreatingRecipe] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recipeName, setRecipeName] = useState("");
  const [recipeDescription, setRecipeDescription] = useState("");
  const [recipePrice, setRecipePrice] = useState("");
  const [recipeCategory, setRecipeCategory] = useState("General");
  const [recipeTags, setRecipeTags] = useState("");
  const [recipeRows, setRecipeRows] = useState<RecipeIngredientRow[]>([
    { ingredientId: "", quantityNeeded: "" },
  ]);
  const [ingredientName, setIngredientName] = useState("");
  const [ingredientDescription, setIngredientDescription] = useState("");
  const [ingredientPricePerUnit, setIngredientPricePerUnit] = useState("");
  const [ingredientCategory, setIngredientCategory] = useState("General");
  const [ingredientStockLevel, setIngredientStockLevel] = useState("");
  const [ingredientMinStock, setIngredientMinStock] = useState("5");
  const [ingredientUnitType, setIngredientUnitType] = useState("pieces");
  const [ingredientTags, setIngredientTags] = useState("");

  async function loadDashboard() {
    setLoadingDashboard(true);
    setError(null);

    try {
      const [ingredientData, dishData] = await Promise.all([getIngredients(), getDishesV2()]);
      setIngredients(ingredientData);
      setDishes(dishData);
    } catch (err) {
      setError("No se pudo cargar el panel v2. Verifica backend y migraciones.");
    } finally {
      setLoadingDashboard(false);
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
    loadDashboard();
    loadAiReasoning();
  }, []);

  async function handleStockChange(ingredientId: number, stockLevel: number) {
    setError(null);
    try {
      await updateIngredientStock(ingredientId, stockLevel);
      await loadDashboard();
    } catch (err) {
      setError("No se pudo actualizar el stock del ingrediente. Intenta nuevamente.");
    }
  }

  async function handleSellDish(dishId: number) {
    setSellingDishId(dishId);
    setError(null);
    setLastSaleMessage(null);
    try {
      const result = await sellDishV2({ dish_id: dishId, quantity: 1, created_by: "admin-ui" });
      setLastSaleMessage(
        `Venta registrada para plato #${result.dish_id}. Raciones restantes: ${result.remaining_available_servings}.`,
      );
      await loadDashboard();
    } catch (err) {
      setError("No se pudo registrar la venta. Revisa stock disponible e intenta nuevamente.");
    } finally {
      setSellingDishId(null);
    }
  }

  function resetRecipeForm() {
    setRecipeName("");
    setRecipeDescription("");
    setRecipePrice("");
    setRecipeCategory("General");
    setRecipeTags("");
    setRecipeRows([{ ingredientId: "", quantityNeeded: "" }]);
  }

  function resetIngredientForm() {
    setIngredientName("");
    setIngredientDescription("");
    setIngredientPricePerUnit("");
    setIngredientCategory("General");
    setIngredientStockLevel("");
    setIngredientMinStock("5");
    setIngredientUnitType("pieces");
    setIngredientTags("");
  }

  function updateRecipeRow(index: number, patch: Partial<RecipeIngredientRow>) {
    setRecipeRows((current) =>
      current.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item)),
    );
  }

  function addRecipeRow() {
    setRecipeRows((current) => [...current, { ingredientId: "", quantityNeeded: "" }]);
  }

  function removeRecipeRow(index: number) {
    setRecipeRows((current) => {
      if (current.length <= 1) return current;
      return current.filter((_, itemIndex) => itemIndex !== index);
    });
  }

  async function handleCreateRecipe(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLastRecipeMessage(null);

    const filteredRows = recipeRows.filter(
      (item) => item.ingredientId.trim() !== "" && item.quantityNeeded.trim() !== "",
    );
    if (!recipeName.trim() || !recipePrice.trim() || filteredRows.length === 0) {
      setError("Completa nombre, precio y al menos un ingrediente con cantidad.");
      return;
    }

    const ingredientIds = filteredRows.map((item) => Number(item.ingredientId));
    if (new Set(ingredientIds).size !== ingredientIds.length) {
      setError("No puedes repetir el mismo ingrediente en la receta.");
      return;
    }

    const ingredientsPayload = filteredRows.map((item) => ({
      ingredient_id: Number(item.ingredientId),
      quantity_needed: Number(item.quantityNeeded),
    }));

    if (ingredientsPayload.some((item) => Number.isNaN(item.quantity_needed) || item.quantity_needed <= 0)) {
      setError("Cada cantidad necesaria debe ser mayor que 0.");
      return;
    }

    setCreatingRecipe(true);
    try {
      const tags = recipeTags
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item.length > 0);

      const created = await createDishV2({
        name: recipeName.trim(),
        description: recipeDescription.trim() || undefined,
        price: Number(recipePrice),
        category: recipeCategory.trim() || "General",
        tags,
        ingredients: ingredientsPayload,
      });

      setLastRecipeMessage(`Receta creada: ${created.name} (ID ${created.id}).`);
      resetRecipeForm();
      await loadDashboard();
    } catch (err) {
      setError("No se pudo crear la receta. Revisa ingredientes y vuelve a intentar.");
    } finally {
      setCreatingRecipe(false);
    }
  }

  async function handleCreateIngredient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLastIngredientMessage(null);

    if (
      !ingredientName.trim() ||
      !ingredientPricePerUnit.trim() ||
      !ingredientStockLevel.trim() ||
      !ingredientUnitType.trim()
    ) {
      setError("Completa nombre, coste, stock inicial y unidad.");
      return;
    }

    const payload = {
      name: ingredientName.trim(),
      description: ingredientDescription.trim() || null,
      price_per_unit: Number(ingredientPricePerUnit),
      category: ingredientCategory.trim() || "General",
      stock_level: Number(ingredientStockLevel),
      min_stock: Number(ingredientMinStock || "5"),
      unit_type: ingredientUnitType.trim(),
      tags: ingredientTags
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item.length > 0),
    };

    if (
      Number.isNaN(payload.price_per_unit) ||
      Number.isNaN(payload.stock_level) ||
      Number.isNaN(payload.min_stock) ||
      payload.price_per_unit < 0 ||
      payload.stock_level < 0 ||
      payload.min_stock < 0
    ) {
      setError("Los valores numéricos del ingrediente deben ser válidos y no negativos.");
      return;
    }

    setCreatingIngredient(true);
    try {
      const created = await createIngredient(payload);
      setLastIngredientMessage(`Ingrediente creado: ${created.name} (ID ${created.id}).`);
      resetIngredientForm();
      await loadDashboard();
    } catch (err) {
      setError("No se pudo crear el ingrediente. Revisa los datos y vuelve a intentar.");
    } finally {
      setCreatingIngredient(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="mb-8 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Panel administrativo</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-900">Control de inventario y simulación</h1>
          <p className="mt-2 text-slate-600">
            Ajusta stock por ingrediente y ejecuta ventas atómicas sobre recetas.
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

      {lastSaleMessage && (
        <div className="mb-6 rounded-3xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-700 shadow-card">
          {lastSaleMessage}
        </div>
      )}

      {lastIngredientMessage && (
        <div className="mb-6 rounded-3xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-700 shadow-card">
          {lastIngredientMessage}
        </div>
      )}

      {lastRecipeMessage && (
        <div className="mb-6 rounded-3xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-700 shadow-card">
          {lastRecipeMessage}
        </div>
      )}

      <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-slate-900">Alta de ingredientes</h2>
          <p className="text-sm text-slate-500">
            Crea productos base que luego podrás usar en las recetas y ventas atomicas.
          </p>
        </div>

        <form className="space-y-4 rounded-2xl border border-slate-200 p-4" onSubmit={handleCreateIngredient}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-700">
              Nombre
              <input
                type="text"
                value={ingredientName}
                onChange={(event) => setIngredientName(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                required
              />
            </label>
            <label className="text-sm text-slate-700">
              Costo por unidad
              <input
                type="number"
                min={0}
                step="0.001"
                value={ingredientPricePerUnit}
                onChange={(event) => setIngredientPricePerUnit(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                required
              />
            </label>
            <label className="text-sm text-slate-700">
              Categoria
              <input
                type="text"
                value={ingredientCategory}
                onChange={(event) => setIngredientCategory(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              />
            </label>
            <label className="text-sm text-slate-700">
              Unidad
              <input
                type="text"
                value={ingredientUnitType}
                onChange={(event) => setIngredientUnitType(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                placeholder="kg, pieces, liters..."
                required
              />
            </label>
            <label className="text-sm text-slate-700">
              Stock inicial
              <input
                type="number"
                min={0}
                step="0.001"
                value={ingredientStockLevel}
                onChange={(event) => setIngredientStockLevel(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                required
              />
            </label>
            <label className="text-sm text-slate-700">
              Stock minimo
              <input
                type="number"
                min={0}
                step="0.001"
                value={ingredientMinStock}
                onChange={(event) => setIngredientMinStock(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              />
            </label>
          </div>

          <label className="block text-sm text-slate-700">
            Descripcion
            <textarea
              value={ingredientDescription}
              onChange={(event) => setIngredientDescription(event.target.value)}
              rows={3}
              className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
            />
          </label>

          <label className="block text-sm text-slate-700">
            Tags (separados por coma)
            <input
              type="text"
              value={ingredientTags}
              onChange={(event) => setIngredientTags(event.target.value)}
              className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
            />
          </label>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={creatingIngredient}
              className="rounded-2xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {creatingIngredient ? "Creando ingrediente..." : "Crear ingrediente"}
            </button>
          </div>
        </form>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Inventario de ingredientes</h2>
            <p className="text-sm text-slate-500">Modifica stock en decimal por unidad base (kg, litros, piezas).</p>
          </div>
          {loadingDashboard && <p className="text-sm text-slate-500">Actualizando panel…</p>}
        </div>

        <div className="mt-6 space-y-4">
          {ingredients.length === 0 ? (
            <p className="text-sm text-slate-500">Todavia no hay ingredientes. Usa el formulario superior para crear el primero.</p>
          ) : (
            ingredients.map((ingredient) => (
              <InventoryRow
                key={ingredient.id}
                ingredient={ingredient}
                onStockChange={handleStockChange}
              />
            ))
          )}
        </div>
      </section>

      <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-slate-900">Editor de recetas</h2>
          <p className="text-sm text-slate-500">
            Define un plato y su composicion de ingredientes para habilitar ventas atomicas.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleCreateRecipe}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-700">
              Nombre del plato
              <input
                type="text"
                value={recipeName}
                onChange={(event) => setRecipeName(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                required
              />
            </label>
            <label className="text-sm text-slate-700">
              Precio de venta
              <input
                type="number"
                min={0}
                step="0.01"
                value={recipePrice}
                onChange={(event) => setRecipePrice(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                required
              />
            </label>
            <label className="text-sm text-slate-700">
              Categoria
              <input
                type="text"
                value={recipeCategory}
                onChange={(event) => setRecipeCategory(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              />
            </label>
            <label className="text-sm text-slate-700">
              Tags (separados por coma)
              <input
                type="text"
                value={recipeTags}
                onChange={(event) => setRecipeTags(event.target.value)}
                className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              />
            </label>
          </div>

          <label className="block text-sm text-slate-700">
            Descripcion
            <textarea
              value={recipeDescription}
              onChange={(event) => setRecipeDescription(event.target.value)}
              rows={3}
              className="mt-1 w-full rounded-2xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
            />
          </label>

          <div className="space-y-3 rounded-2xl border border-slate-200 p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-800">Ingredientes de la receta</p>
              <button
                type="button"
                onClick={addRecipeRow}
                className="rounded-xl border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100"
              >
                Agregar ingrediente
              </button>
            </div>

            {recipeRows.map((row, index) => (
              <div key={`${index}-${row.ingredientId}`} className="grid gap-3 md:grid-cols-[2fr_1fr_auto]">
                <select
                  value={row.ingredientId}
                  onChange={(event) => updateRecipeRow(index, { ingredientId: event.target.value })}
                  className="rounded-2xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                >
                  <option value="">Selecciona ingrediente</option>
                  {ingredients.map((ingredient) => (
                    <option key={ingredient.id} value={ingredient.id}>
                      {ingredient.name} ({ingredient.unit_type})
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  min={0}
                  step="0.001"
                  placeholder="Cantidad necesaria"
                  value={row.quantityNeeded}
                  onChange={(event) =>
                    updateRecipeRow(index, { quantityNeeded: event.target.value })
                  }
                  className="rounded-2xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                />
                <button
                  type="button"
                  onClick={() => removeRecipeRow(index)}
                  className="rounded-2xl border border-rose-300 px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-50"
                >
                  Quitar
                </button>
              </div>
            ))}
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={creatingRecipe}
              className="rounded-2xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {creatingRecipe ? "Guardando receta..." : "Guardar receta"}
            </button>
          </div>
        </form>
      </section>

      <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
          <h2 className="text-xl font-semibold text-slate-900">Recetas y disponibilidad real</h2>
          <p className="mt-2 text-slate-500">
            Cada venta descuenta todos los ingredientes de forma atomica.
          </p>
          <div className="mt-6 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3">Plato</th>
                  <th className="px-4 py-3">Disponibles</th>
                  <th className="px-4 py-3">Margen</th>
                  <th className="px-4 py-3">Accion</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {dishes.length === 0 ? (
                  <tr>
                    <td className="px-4 py-3 text-slate-500" colSpan={4}>
                      Aun no hay platos v2. Crea ingredientes y luego recetas en este panel.
                    </td>
                  </tr>
                ) : (
                  dishes.map((dish) => (
                    <tr key={dish.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-900">{dish.name}</td>
                      <td className="px-4 py-3">{dish.available_servings}</td>
                      <td className="px-4 py-3">€{Number(dish.margin).toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          disabled={dish.available_servings <= 0 || sellingDishId === dish.id}
                          onClick={() => handleSellDish(dish.id)}
                          className="rounded-2xl bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                        >
                          {sellingDishId === dish.id ? "Vendiendo..." : "Vender 1"}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
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
