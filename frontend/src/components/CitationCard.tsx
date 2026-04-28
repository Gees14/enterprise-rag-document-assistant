import { useState } from 'react'
import type { SourceReference } from '../types'

interface CitationCardProps {
  source: SourceReference
  index: number
}

export default function CitationCard({ source, index }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false)
  const scorePercent = Math.round(source.score * 100)

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden text-sm">
      {/* Header */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-slate-700/40 transition-colors"
      >
        {/* Rank badge */}
        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600/20 border border-blue-600/50 text-blue-400 text-xs flex items-center justify-center font-bold">
          {index + 1}
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-slate-200 truncate">{source.document_name}</span>
            <span className="text-xs text-slate-500">Page {source.page_number}</span>
            <span
              className={`ml-auto text-xs px-2 py-0.5 rounded font-mono ${
                scorePercent >= 70
                  ? 'bg-emerald-900/40 text-emerald-400'
                  : scorePercent >= 40
                  ? 'bg-yellow-900/40 text-yellow-400'
                  : 'bg-slate-700 text-slate-400'
              }`}
            >
              {scorePercent}%
            </span>
          </div>
          {!expanded && (
            <p className="mt-1 text-slate-400 text-xs line-clamp-2">{source.snippet}</p>
          )}
        </div>

        <span className="text-slate-500 text-xs ml-2 flex-shrink-0">
          {expanded ? '▲' : '▼'}
        </span>
      </button>

      {/* Expanded snippet */}
      {expanded && (
        <div className="px-4 pb-4 pt-1 border-t border-slate-700">
          <p className="text-slate-300 text-xs leading-relaxed font-mono whitespace-pre-wrap">
            {source.snippet}
          </p>
          <div className="mt-2 flex gap-4 text-xs text-slate-500">
            <span>Chunk: <code className="text-slate-400">{source.chunk_id}</code></span>
            <span>Score: <code className="text-slate-400">{source.score.toFixed(4)}</code></span>
          </div>
        </div>
      )}
    </div>
  )
}
