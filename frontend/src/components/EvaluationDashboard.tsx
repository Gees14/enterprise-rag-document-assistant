import { useState } from 'react'
import { runEvaluation } from '../services/api'
import type { EvalRunResponse } from '../types'

function MetricCard({ label, value, description }: { label: string; value: string; description: string }) {
  return (
    <div className="rounded-xl bg-slate-800 border border-slate-700 p-4">
      <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-100 mb-1">{value}</p>
      <p className="text-xs text-slate-500">{description}</p>
    </div>
  )
}

export default function EvaluationDashboard() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<EvalRunResponse | null>(null)
  const [topK, setTopK] = useState(5)

  const handleRun = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await runEvaluation(topK)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evaluation failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center gap-4">
        <div>
          <label className="text-xs text-slate-500 block mb-1">Top-k for retrieval</label>
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-slate-300 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {[3, 5, 8, 10].map((k) => (
              <option key={k} value={k}>top-{k}</option>
            ))}
          </select>
        </div>
        <div className="pt-4">
          <button
            onClick={handleRun}
            disabled={loading}
            className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium transition-colors flex items-center gap-2"
          >
            {loading && (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            )}
            {loading ? 'Running evaluation…' : 'Run Evaluation'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-red-900/30 border border-red-800 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && (
        <div className="text-center py-16 text-slate-500 text-sm">
          <div className="text-3xl mb-3">📊</div>
          <p>Click "Run Evaluation" to compute RAG metrics against the question set.</p>
          <p className="text-xs mt-2 text-slate-600">Requires indexed documents and data/eval/questions.json.</p>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {/* Metric cards */}
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            <MetricCard
              label="Precision@k"
              value={`${(result.metrics.precision_at_k * 100).toFixed(1)}%`}
              description="Relevant chunks in top-k"
            />
            <MetricCard
              label="Recall@k"
              value={`${(result.metrics.recall_at_k * 100).toFixed(1)}%`}
              description="Relevant pages found"
            />
            <MetricCard
              label="MRR"
              value={result.metrics.mean_reciprocal_rank.toFixed(3)}
              description="Mean reciprocal rank"
            />
            <MetricCard
              label="Keyword Coverage"
              value={`${(result.metrics.avg_keyword_coverage * 100).toFixed(1)}%`}
              description="Expected keywords found"
            />
            <MetricCard
              label="Avg Latency"
              value={`${result.metrics.avg_latency_ms.toFixed(0)} ms`}
              description="Retrieval latency"
            />
          </div>

          {/* Summary */}
          <div className="rounded-xl bg-slate-800 border border-slate-700 px-4 py-3 text-sm text-slate-400">
            Evaluated <strong className="text-slate-200">{result.metrics.total_questions}</strong> questions ·{' '}
            <strong className="text-slate-200">{result.metrics.questions_with_relevant_doc}</strong> retrieved relevant document ·{' '}
            Run at {new Date(result.eval_timestamp).toLocaleString()}
          </div>

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recommendations</h3>
              {result.recommendations.map((rec, i) => (
                <div key={i} className="rounded-lg bg-slate-800/50 border border-slate-700 px-4 py-3 text-sm">
                  <span className="font-mono text-blue-400 text-xs">{rec.metric}</span>
                  <p className="text-slate-300 mt-1">{rec.recommendation}</p>
                </div>
              ))}
            </div>
          )}

          {/* Per-question table */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Per-Question Results</h3>
            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-slate-800/60 text-slate-400 uppercase tracking-wider">
                    <th className="text-left px-4 py-3">Question</th>
                    <th className="text-left px-4 py-3">Relevant Doc?</th>
                    <th className="text-left px-4 py-3">MRR</th>
                    <th className="text-left px-4 py-3">Keywords</th>
                    <th className="text-left px-4 py-3">Score</th>
                    <th className="text-left px-4 py-3">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {result.per_question_results.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="px-4 py-2 text-slate-300 max-w-[250px] truncate" title={r.question}>
                        {r.question}
                      </td>
                      <td className="px-4 py-2">
                        <span className={r.relevant_doc_retrieved ? 'text-emerald-400' : 'text-red-400'}>
                          {r.relevant_doc_retrieved ? '✓' : '✗'}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-slate-400">{r.reciprocal_rank.toFixed(2)}</td>
                      <td className="px-4 py-2 text-slate-400">
                        {(r.keyword_coverage * 100).toFixed(0)}%
                        {r.keyword_misses.length > 0 && (
                          <span className="text-red-400 ml-1 text-xs" title={`Missing: ${r.keyword_misses.join(', ')}`}>
                            (-{r.keyword_misses.length})
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-2 text-slate-400">{r.top_score.toFixed(3)}</td>
                      <td className="px-4 py-2 text-slate-400">{r.latency_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
