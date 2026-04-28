// ─────────────────────────────────────────────
// Document types
// ─────────────────────────────────────────────

export type DocumentStatus = 'uploaded' | 'indexing' | 'indexed' | 'failed'

export interface Document {
  id: string
  filename: string
  upload_time: string
  status: DocumentStatus
  page_count: number
  chunk_count: number
  file_size_bytes: number
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
}

export interface UploadResponse {
  document_id: string
  filename: string
  status: DocumentStatus
  file_size_bytes: number
  message: string
}

export interface IndexResponse {
  document_id: string
  filename: string
  status: DocumentStatus
  chunk_count: number
  page_count: number
  message: string
}

export interface DeleteResponse {
  document_id: string
  message: string
}

// ─────────────────────────────────────────────
// Chat types
// ─────────────────────────────────────────────

export interface ChatRequest {
  question: string
  top_k?: number
}

export interface SourceReference {
  document_name: string
  page_number: number
  chunk_id: string
  snippet: string
  score: number
}

export interface RetrievedChunk {
  chunk_id: string
  document_id: string
  filename: string
  page_number: number
  text: string
  score: number
}

export interface ChatResponse {
  answer: string
  confidence: number
  sources: SourceReference[]
  retrieved_chunks: RetrievedChunk[]
  latency_ms: number
  mode: 'retrieval_only' | 'llm_generated'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  response?: ChatResponse
}

// ─────────────────────────────────────────────
// Evaluation types
// ─────────────────────────────────────────────

export interface EvalMetrics {
  precision_at_k: number
  recall_at_k: number
  mean_reciprocal_rank: number
  avg_keyword_coverage: number
  avg_latency_ms: number
  total_questions: number
  questions_with_relevant_doc: number
}

export interface PerQuestionResult {
  question: string
  retrieved_documents: string[]
  retrieved_pages: number[]
  keyword_hits: string[]
  keyword_misses: string[]
  keyword_coverage: number
  reciprocal_rank: number
  top_score: number
  latency_ms: number
  relevant_doc_retrieved: boolean
}

export interface EvalRecommendation {
  metric: string
  value: number
  recommendation: string
}

export interface EvalRunResponse {
  metrics: EvalMetrics
  per_question_results: PerQuestionResult[]
  recommendations: EvalRecommendation[]
  eval_timestamp: string
}

// ─────────────────────────────────────────────
// Health types
// ─────────────────────────────────────────────

export interface HealthResponse {
  status: string
  version: string
  app_name: string
}

export interface ReadinessResponse {
  status: string
  vector_store: string
  chunk_count: number
  llm_enabled: boolean
}

// ─────────────────────────────────────────────
// UI state types
// ─────────────────────────────────────────────

export interface ApiError {
  error: string
  type: string
}
