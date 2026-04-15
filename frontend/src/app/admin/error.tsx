"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Admin page error:", error);
  }, [error]);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Error</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-900">Algo salió mal</h1>
      </div>

      <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 shadow-card">
        <p className="mb-4 text-rose-700">
          {error.message || "Ocurrió un error al cargar el panel de administración."}
        </p>
        <button
          onClick={() => reset()}
          className="rounded-2xl bg-rose-600 px-6 py-2 font-semibold text-white hover:bg-rose-700 transition"
        >
          Intentar nuevamente
        </button>
      </div>

      {error.digest && (
        <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs text-slate-500">
            <strong>Error ID:</strong> {error.digest}
          </p>
        </div>
      )}
    </main>
  );
}
