import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Evaluation from './pages/Evaluation'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/evaluation" element={<Evaluation />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
