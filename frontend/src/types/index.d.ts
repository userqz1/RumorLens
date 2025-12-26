// Type definitions for RumorLens

export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface AnalysisResult {
  keywords: string[]
  sentiment: string
  category: string
  sources: string[]
  fact_check_points: string[]
  risk_indicators: string[]
}

export interface Detection {
  id: string
  content: string
  is_rumor: boolean
  confidence: number
  risk_level: RiskLevel
  explanation: string
  analysis?: AnalysisResult
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OverviewStats {
  total_detections: number
  total_rumors: number
  total_verified: number
  rumor_rate: number
  avg_confidence: number
}

export interface TrendDataPoint {
  date: string
  rumors: number
  verified: number
  total: number
}

export interface CategoryStats {
  category: string
  count: number
  percentage: number
}

export interface KeywordStats {
  keyword: string
  count: number
  weight: number
}

export interface RiskDistribution {
  low: number
  medium: number
  high: number
  critical: number
}

export interface PropagationNode {
  node_id: string
  parent_id?: string
  content?: string
  user_info?: Record<string, any>
  engagement?: Record<string, any>
  timestamp?: string
}
