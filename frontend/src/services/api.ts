import axios, { AxiosError } from 'axios'
import type {
  ChatRequest,
  ChatResponse,
  DeleteResponse,
  DocumentListResponse,
  EvalRunResponse,
  HealthResponse,
  IndexResponse,
  ReadinessResponse,
  UploadResponse,
} from '../types'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
})

// ─────────────────────────────────────────────
// Error handling
// ─────────────────────────────────────────────

function extractErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    return (
      error.response?.data?.error ??
      error.response?.data?.detail ??
      error.message ??
      'An unknown error occurred.'
    )
  }
  if (error instanceof Error) return error.message
  return 'An unknown error occurred.'
}

// ─────────────────────────────────────────────
// Health
// ─────────────────────────────────────────────

export async function getHealth(): Promise<HealthResponse> {
  const res = await client.get<HealthResponse>('/health')
  return res.data
}

export async function getReadiness(): Promise<ReadinessResponse> {
  const res = await client.get<ReadinessResponse>('/health/ready')
  return res.data
}

// ─────────────────────────────────────────────
// Documents
// ─────────────────────────────────────────────

export async function uploadDocuments(files: File[]): Promise<UploadResponse[]> {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  try {
    const res = await client.post<UploadResponse[]>('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  } catch (err) {
    throw new Error(extractErrorMessage(err))
  }
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const res = await client.get<DocumentListResponse>('/documents')
  return res.data
}

export async function indexDocument(documentId: string): Promise<IndexResponse> {
  try {
    const res = await client.post<IndexResponse>(`/documents/${documentId}/index`)
    return res.data
  } catch (err) {
    throw new Error(extractErrorMessage(err))
  }
}

export async function deleteDocument(documentId: string): Promise<DeleteResponse> {
  try {
    const res = await client.delete<DeleteResponse>(`/documents/${documentId}`)
    return res.data
  } catch (err) {
    throw new Error(extractErrorMessage(err))
  }
}

// ─────────────────────────────────────────────
// Chat
// ─────────────────────────────────────────────

export async function queryChat(request: ChatRequest): Promise<ChatResponse> {
  try {
    const res = await client.post<ChatResponse>('/chat/query', request)
    return res.data
  } catch (err) {
    throw new Error(extractErrorMessage(err))
  }
}

// ─────────────────────────────────────────────
// Evaluation
// ─────────────────────────────────────────────

export async function runEvaluation(topK = 5): Promise<EvalRunResponse> {
  try {
    const res = await client.post<EvalRunResponse>('/eval/run', null, {
      params: { top_k: topK },
    })
    return res.data
  } catch (err) {
    throw new Error(extractErrorMessage(err))
  }
}
