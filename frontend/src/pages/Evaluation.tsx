import EvaluationDashboard from '../components/EvaluationDashboard'

export default function Evaluation() {
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-100">RAG Evaluation</h1>
        <p className="text-sm text-slate-500 mt-1">
          Run retrieval quality metrics against the evaluation question set (
          <code className="text-slate-400 text-xs">data/eval/questions.json</code>).
        </p>
      </div>

      {/* Metric descriptions */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        {[
          { name: 'Precision@k', desc: 'Fraction of top-k retrieved chunks from the relevant document.' },
          { name: 'Recall@k', desc: 'Fraction of relevant pages successfully retrieved in top-k.' },
          { name: 'MRR', desc: 'Mean Reciprocal Rank — how high does the first relevant result appear?' },
          { name: 'Keyword Coverage', desc: 'Average fraction of expected keywords found in retrieved text.' },
        ].map((m) => (
          <div key={m.name} className="rounded-lg bg-slate-800/50 border border-slate-800 px-3 py-2">
            <p className="text-xs font-semibold text-blue-400 mb-0.5">{m.name}</p>
            <p className="text-xs text-slate-500">{m.desc}</p>
          </div>
        ))}
      </div>

      <EvaluationDashboard />
    </div>
  )
}
