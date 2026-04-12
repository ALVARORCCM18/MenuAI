import type { Product } from "@/types";

type DishCardProps = {
  dish: Product;
  rank: number;
};

export function DishCard({ dish, rank }: DishCardProps) {
  const isTopThree = rank <= 3;
  return (
    <article className={`rounded-3xl border p-6 shadow-card transition duration-300 ${isTopThree ? "border-amber-300 bg-amber-50" : "border-slate-200 bg-white"}`}>
      <div className="mb-4 flex items-center justify-between gap-4">
        <span className="inline-flex items-center rounded-full bg-slate-900 px-3 py-1 text-sm font-semibold text-white">
          #{rank}
        </span>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs uppercase tracking-[0.24em] text-slate-600">
          {dish.category}
        </span>
      </div>
      <h2 className="mb-2 text-xl font-semibold text-slate-900">{dish.name}</h2>
      <p className="mb-4 text-sm leading-6 text-slate-600">{dish.description}</p>
      <div className="mb-4 flex flex-wrap gap-2">
        {dish.tags.map((tag) => (
          <span key={tag} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700">
            {tag}
          </span>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Precio</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">€{dish.price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Margen</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">€{dish.margin.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Stock</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">{dish.stock_level}</p>
        </div>
      </div>
    </article>
  );
}
