"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global error:", error);
  }, [error]);

  return (
    <html lang="es">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-8">
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Error Global</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">La aplicación encontró un problema</h1>
          </div>

          <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 shadow-lg">
            <p className="mb-4 font-mono text-sm text-rose-700">
              {error.message || "Error desconocido en la aplicación"}
            </p>
            <p className="mb-4 text-rose-600 text-sm">
              Por favor, intenta recargar la página.
            </p>
            <button
              onClick={() => reset()}
              className="rounded-2xl bg-rose-600 px-6 py-2 font-semibold text-white hover:bg-rose-700 transition"
            >
              Reintentar
            </button>
          </div>

          {error.stack && (
            <details className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <summary className="cursor-pointer text-xs font-mono text-slate-600">
                Detalles técnicos
              </summary>
              <pre className="mt-4 whitespace-pre-wrap break-words font-mono text-xs text-slate-700 overflow-auto max-h-60">
                {error.stack}
              </pre>
            </details>
          )}
        </main>
      </body>
    </html>
  );
}
