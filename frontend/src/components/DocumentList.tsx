import { useEffect, useState } from 'react'
import { deleteDocument, indexDocument, listDocuments } from '../services/api'
import type { Document } from '../types'

interface DocumentListProps {
  refreshTrigger: number
}

const STATUS_STYLES: Record<string, string> = {
  uploaded: 'bg-yellow-900/40 text-yellow-300 border-yellow-700',
  indexing: 'bg-blue-900/40 text-blue-300 border-blue-700',
  indexed: 'bg-emerald-900/40 text-emerald-300 border-emerald-700',
  failed: 'bg-red-900/40 text-red-300 border-red-700',
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function DocumentList({ refreshTrigger }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionMap, setActionMap] = useState<Record<string, string>>({})

  const fetchDocuments = async () => {
    try {
      const data = await listDocuments()
      setDocuments(data.documents)
      setError(null)
    } catch (err) {
      setError('Could not load documents.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchDocuments() }, [refreshTrigger])

  const handleIndex = async (doc: Document) => {
    setActionMap((m) => ({ ...m, [doc.id]: 'indexing' }))
    try {
      await indexDocument(doc.id)
      await fetchDocuments()
    } catch (err) {
      setActionMap((m) => ({ ...m, [doc.id]: 'error' }))
    } finally {
      setActionMap((m) => { const n = { ...m }; delete n[doc.id]; return n })
    }
  }

  const handleDelete = async (doc: Document) => {
    if (!confirm(`Delete "${doc.filename}" and all its indexed chunks?`)) return
    setActionMap((m) => ({ ...m, [doc.id]: 'deleting' }))
    try {
      await deleteDocument(doc.id)
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
    } catch {
      setActionMap((m) => { const n = { ...m }; delete n[doc.id]; return n })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-slate-500 text-sm">
        <div className="w-5 h-5 border-2 border-slate-500 border-t-transparent rounded-full animate-spin mr-2" />
        Loading documents…
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-900/30 border border-red-800 px-4 py-3 text-sm text-red-300">
        {error}
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500 text-sm">
        No documents uploaded yet. Drop a PDF above to get started.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider">
            <th className="text-left px-4 py-3">Document</th>
            <th className="text-left px-4 py-3">Status</th>
            <th className="text-left px-4 py-3">Chunks</th>
            <th className="text-left px-4 py-3">Pages</th>
            <th className="text-left px-4 py-3">Size</th>
            <th className="text-left px-4 py-3">Uploaded</th>
            <th className="text-left px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {documents.map((doc) => {
            const action = actionMap[doc.id]
            return (
              <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-4 py-3 font-mono text-slate-300 max-w-[200px] truncate" title={doc.filename}>
                  {doc.filename}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex px-2 py-0.5 rounded border text-xs font-medium ${STATUS_STYLES[doc.status] ?? STATUS_STYLES.uploaded}`}>
                    {action === 'indexing' ? 'indexing…' : doc.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-400">{doc.chunk_count}</td>
                <td className="px-4 py-3 text-slate-400">{doc.page_count}</td>
                <td className="px-4 py-3 text-slate-400">{formatBytes(doc.file_size_bytes)}</td>
                <td className="px-4 py-3 text-slate-400">{formatDate(doc.upload_time)}</td>
                <td className="px-4 py-3 flex gap-2">
                  {doc.status !== 'indexed' && doc.status !== 'indexing' && (
                    <button
                      onClick={() => handleIndex(doc)}
                      disabled={!!action}
                      className="text-xs px-2 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 transition-colors"
                    >
                      Index
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(doc)}
                    disabled={!!action}
                    className="text-xs px-2 py-1 rounded bg-slate-700 hover:bg-red-800 text-slate-300 disabled:opacity-50 transition-colors"
                  >
                    {action === 'deleting' ? '…' : 'Delete'}
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
