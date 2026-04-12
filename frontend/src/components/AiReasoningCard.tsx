type AiReasoningCardProps = {
  aiReasoning: string;
  loading?: boolean;
};

export function AiReasoningCard({ aiReasoning, loading = false }: AiReasoningCardProps) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <h2 className="text-lg font-semibold text-slate-900">Razonamiento de IA</h2>
      <p className="mt-2 text-sm text-slate-500">La IA explica por qué se prioriza la carta actual.</p>

      <div className="mt-5 rounded-3xl bg-slate-50 p-5 text-slate-800">
        {loading ? (
          <p>Cargando explicación...</p>
        ) : (
          <p className="whitespace-pre-line text-sm leading-7">{aiReasoning}</p>
        )}
      </div>
    </div>
  );
}
