import { useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Evaluation from './pages/Evaluation'
import type { ChatMessage } from './types'

export default function App() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={<Dashboard chatMessages={chatMessages} setChatMessages={setChatMessages} />}
          />
          <Route path="/evaluation" element={<Evaluation />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
