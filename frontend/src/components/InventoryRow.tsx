import { useEffect, useState } from "react";
import type { Product } from "@/types";

type InventoryRowProps = {
  product: Product;
  onStockChange: (productId: number, stockLevel: number) => void;
};

export function InventoryRow({ product, onStockChange }: InventoryRowProps) {
  const [value, setValue] = useState(product.stock_level.toString());

  useEffect(() => {
    setValue(product.stock_level.toString());
  }, [product.stock_level]);

  return (
    <div className="grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-[1fr_auto_auto]">
      <div>
        <p className="font-semibold text-slate-900">{product.name}</p>
        <p className="text-sm text-slate-500">{product.category}</p>
      </div>
      <div className="flex items-center gap-3">
        <label className="sr-only" htmlFor={`stock-${product.id}`}>
          Stock del producto
        </label>
        <input
          id={`stock-${product.id}`}
          type="number"
          min={0}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          className="w-24 rounded-2xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
        />
      </div>
      <button
        type="button"
        onClick={() => onStockChange(product.id, Number(value))}
        className="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
      >
        Guardar
      </button>
    </div>
  );
}
