import { useEffect, useRef, useState } from 'react'
import { queryChat } from '../services/api'
import type { ChatMessage, ChatResponse } from '../types'
import CitationCard from './CitationCard'

let messageIdCounter = 0
const newId = () => String(++messageIdCounter)

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [topK, setTopK] = useState(5)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    const question = input.trim()
    if (!question || loading) return

    const userMsg: ChatMessage = {
      id: newId(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setError(null)
    setLoading(true)

    try {
      const response = await queryChat({ question, top_k: topK })
      const assistantMsg: ChatMessage = {
        id: newId(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        response,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Message thread */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6 min-h-0">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-slate-500 text-sm text-center px-8">
            <div>
              <div className="text-3xl mb-3">💬</div>
              <p className="font-medium text-slate-400 mb-1">Ask a question</p>
              <p>Upload and index a PDF, then ask anything about its content.</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] space-y-3 ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
              {/* Bubble */}
              <div
                className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-slate-800 text-slate-200 rounded-bl-sm border border-slate-700'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>

              {/* Metadata for assistant messages */}
              {msg.role === 'assistant' && msg.response && (
                <div className="w-full space-y-3">
                  {/* Stats row */}
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                      {msg.response.mode === 'llm_generated' ? '🤖 LLM' : '🔍 Retrieval-only'}
                    </span>
                    <span>Confidence: {Math.round(msg.response.confidence * 100)}%</span>
                    <span>{msg.response.latency_ms} ms</span>
                    <span>{msg.response.sources.length} sources</span>
                  </div>

                  {/* Citations */}
                  {msg.response.sources.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Sources</p>
                      {msg.response.sources.map((src, i) => (
                        <CitationCard key={src.chunk_id} source={src} index={i} />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 px-4 py-3 rounded-2xl rounded-bl-sm">
              <div className="flex gap-1 items-center">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" />
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg bg-red-900/30 border border-red-800 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-slate-800 px-4 py-3 bg-slate-900/50">
        <div className="flex items-end gap-2">
          {/* Top-k selector */}
          <div className="flex-shrink-0">
            <label className="text-xs text-slate-500 block mb-1">Top-k</label>
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {[3, 5, 8, 10].map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </div>

          {/* Text input */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents… (Enter to send)"
            rows={2}
            className="flex-1 resize-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-slate-500"
          />

          {/* Send button */}
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 h-10 w-10 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white flex items-center justify-center transition-colors"
            title="Send (Enter)"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
