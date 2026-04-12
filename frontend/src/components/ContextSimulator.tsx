type ContextSimulatorProps = {
  weather: string;
  time: string;
  buttonLabel?: string;
  onContextChange: (next: { weather: string; time: string }) => void;
};

const weatherOptions = ["Soleado", "Lluvia", "Frío"];
const timeOptions = ["Mañana", "Tarde", "Noche"];

export function ContextSimulator({ weather, time, buttonLabel = "Aplicar contexto", onContextChange }: ContextSimulatorProps) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <h2 className="text-lg font-semibold text-slate-900">Simulador de contexto</h2>
      <p className="mt-2 text-sm text-slate-500">Ajusta clima y franja horaria para ver el menú inteligente.</p>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="space-y-2 text-sm text-slate-700">
          Clima
          <select
            value={weather}
            onChange={(event) => onContextChange({ weather: event.target.value, time })}
            className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
          >
            {weatherOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2 text-sm text-slate-700">
          Hora
          <select
            value={time}
            onChange={(event) => onContextChange({ weather, time: event.target.value })}
            className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
          >
            {timeOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={() => onContextChange({ weather, time })}
        className="mt-5 w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
      >
        {buttonLabel}
      </button>
    </div>
  );
}
