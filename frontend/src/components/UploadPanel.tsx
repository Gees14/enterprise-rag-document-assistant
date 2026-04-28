import { useRef, useState } from 'react'
import { indexDocument, uploadDocuments } from '../services/api'
import type { UploadResponse } from '../types'

interface UploadPanelProps {
  onUploadComplete: () => void
}

export default function UploadPanel({ onUploadComplete }: UploadPanelProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploaded, setUploaded] = useState<UploadResponse[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    const pdfFiles = Array.from(files).filter((f) => f.type === 'application/pdf' || f.name.endsWith('.pdf'))
    if (pdfFiles.length === 0) {
      setError('Only PDF files are accepted.')
      return
    }

    setError(null)
    setUploading(true)
    setUploaded([])
    try {
      const responses = await uploadDocuments(pdfFiles)
      setUploaded(responses)

      // Auto-index immediately after upload
      setIndexing(true)
      await Promise.all(responses.map((r) => indexDocument(r.document_id)))
      onUploadComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.')
    } finally {
      setUploading(false)
      setIndexing(false)
    }
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  const loading = uploading || indexing

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-slate-700 hover:border-slate-500 hover:bg-slate-800/50'
        } ${loading ? 'pointer-events-none opacity-60' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />

        {loading ? (
          <div className="space-y-2">
            <div className="flex justify-center">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-sm text-slate-400">
              {uploading ? 'Uploading…' : 'Indexing document chunks…'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-3xl">📄</div>
            <p className="text-sm font-medium text-slate-300">
              Drop PDF files here, or click to browse
            </p>
            <p className="text-xs text-slate-500">
              Multiple files supported · Max 50 MB each · Text-based PDFs only
            </p>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-red-900/40 border border-red-700 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Success */}
      {uploaded.length > 0 && !loading && (
        <div className="rounded-lg bg-emerald-900/40 border border-emerald-700 px-4 py-3 space-y-1">
          <p className="text-sm font-medium text-emerald-300">
            {uploaded.length} document{uploaded.length > 1 ? 's' : ''} uploaded and indexed
          </p>
          {uploaded.map((u) => (
            <p key={u.document_id} className="text-xs text-emerald-400 font-mono">
              ✓ {u.filename}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}
