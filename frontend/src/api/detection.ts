import api from './index'
import type { Detection, PaginatedResponse, AnalysisResult, PropagationNode } from '@/types'

export interface DetectionRequest {
  content: string
  include_analysis?: boolean
  include_propagation?: boolean
}

export interface BatchDetectionRequest {
  contents: string[]
  include_analysis?: boolean
}

export interface BatchDetectionResponse {
  total: number
  success: number
  failed: number
  results: Detection[]
}

export interface HistoryFilters {
  page?: number
  page_size?: number
  is_rumor?: boolean
  risk_level?: string
  start_date?: string
  end_date?: string
}

export interface PropagationResponse {
  detection_id: string
  nodes: PropagationNode[]
  pattern?: string
  spread_speed?: string
  estimated_reach?: number
  influence_score?: number
}

export const detectionApi = {
  async detectSingle(data: DetectionRequest): Promise<Detection> {
    const response = await api.post<Detection>('/detection/single', data)
    return response.data
  },

  async detectBatch(data: BatchDetectionRequest): Promise<BatchDetectionResponse> {
    const response = await api.post<BatchDetectionResponse>('/detection/batch', data)
    return response.data
  },

  async getDetection(id: string): Promise<Detection> {
    const response = await api.get<Detection>(`/detection/${id}`)
    return response.data
  },

  async getAnalysis(id: string): Promise<AnalysisResult> {
    const response = await api.get<AnalysisResult>(`/detection/${id}/analysis`)
    return response.data
  },

  async getPropagation(id: string): Promise<PropagationResponse> {
    const response = await api.get<PropagationResponse>(`/detection/${id}/propagation`)
    return response.data
  },

  async getHistory(filters: HistoryFilters = {}): Promise<PaginatedResponse<Detection>> {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())
    if (filters.is_rumor !== undefined) params.append('is_rumor', filters.is_rumor.toString())
    if (filters.risk_level) params.append('risk_level', filters.risk_level)
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)

    const response = await api.get<PaginatedResponse<Detection>>(`/history?${params.toString()}`)
    return response.data
  },

  async deleteDetection(id: string): Promise<void> {
    await api.delete(`/history/${id}`)
  },

  async deleteMultiple(ids: string[]): Promise<void> {
    await api.delete('/history/batch', { data: { ids } })
  },
}
