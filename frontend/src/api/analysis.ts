import api from './index'
import type { OverviewStats, TrendDataPoint, CategoryStats, KeywordStats, RiskDistribution } from '@/types'

export interface TrendResponse {
  data: TrendDataPoint[]
  period: string
}

export interface CategoryResponse {
  data: CategoryStats[]
  total: number
}

export interface KeywordsResponse {
  data: KeywordStats[]
  total_keywords: number
}

export interface RiskDistributionResponse {
  distribution: RiskDistribution
  total: number
}

export const analysisApi = {
  async getOverview(): Promise<OverviewStats> {
    const response = await api.get<OverviewStats>('/analysis/overview')
    return response.data
  },

  async getTrend(days: number = 30): Promise<TrendResponse> {
    const response = await api.get<TrendResponse>(`/analysis/trend?days=${days}`)
    return response.data
  },

  async getCategories(): Promise<CategoryResponse> {
    const response = await api.get<CategoryResponse>('/analysis/category')
    return response.data
  },

  async getKeywords(limit: number = 50): Promise<KeywordsResponse> {
    const response = await api.get<KeywordsResponse>(`/analysis/keywords?limit=${limit}`)
    return response.data
  },

  async getRiskDistribution(): Promise<RiskDistributionResponse> {
    const response = await api.get<RiskDistributionResponse>('/analysis/risk-distribution')
    return response.data
  },
}
