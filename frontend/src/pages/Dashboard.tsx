import { useState } from 'react'
import ChatPanel from '../components/ChatPanel'
import DocumentList from '../components/DocumentList'
import UploadPanel from '../components/UploadPanel'
import type { ChatMessage } from '../types'

interface DashboardProps {
  chatMessages: ChatMessage[]
  setChatMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>
}

export default function Dashboard({ chatMessages, setChatMessages }: DashboardProps) {
  const [refreshCounter, setRefreshCounter] = useState(0)

  const handleUploadComplete = () => {
    setRefreshCounter((c) => c + 1)
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left column: Document management */}
      <div className="w-[480px] flex-shrink-0 flex flex-col border-r border-slate-800 overflow-y-auto">
        <div className="px-6 py-5 border-b border-slate-800">
          <h1 className="text-lg font-semibold text-slate-100">Documents</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Upload PDFs to index and query
          </p>
        </div>

        <div className="p-5 border-b border-slate-800">
          <UploadPanel onUploadComplete={handleUploadComplete} />
        </div>

        <div className="p-5 flex-1">
          <h2 className="text-xs text-slate-500 uppercase tracking-wider mb-3">Indexed Documents</h2>
          <DocumentList refreshTrigger={refreshCounter} />
        </div>
      </div>

      {/* Right column: Chat */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-slate-100">Chat</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Ask questions about your indexed documents
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            RAG Active
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <ChatPanel messages={chatMessages} setMessages={setChatMessages} />
        </div>
      </div>
    </div>
  )
}
