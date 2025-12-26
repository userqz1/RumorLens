import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { OverviewStats, TrendDataPoint, CategoryStats, KeywordStats, RiskDistribution } from '@/types'
import { analysisApi } from '@/api/analysis'

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const overview = ref<OverviewStats | null>(null)
  const trendData = ref<TrendDataPoint[]>([])
  const categories = ref<CategoryStats[]>([])
  const keywords = ref<KeywordStats[]>([])
  const riskDistribution = ref<RiskDistribution | null>(null)
  const loading = ref(false)

  // Actions
  async function fetchOverview() {
    loading.value = true
    try {
      overview.value = await analysisApi.getOverview()
      return overview.value
    } finally {
      loading.value = false
    }
  }

  async function fetchTrend(days = 30) {
    loading.value = true
    try {
      const result = await analysisApi.getTrend(days)
      trendData.value = result.data
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    loading.value = true
    try {
      const result = await analysisApi.getCategories()
      categories.value = result.data
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchKeywords(limit = 50) {
    loading.value = true
    try {
      const result = await analysisApi.getKeywords(limit)
      keywords.value = result.data
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchRiskDistribution() {
    loading.value = true
    try {
      const result = await analysisApi.getRiskDistribution()
      riskDistribution.value = result.distribution
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchAll() {
    loading.value = true
    try {
      await Promise.all([
        fetchOverview(),
        fetchTrend(),
        fetchCategories(),
        fetchKeywords(),
        fetchRiskDistribution(),
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    overview,
    trendData,
    categories,
    keywords,
    riskDistribution,
    loading,
    // Actions
    fetchOverview,
    fetchTrend,
    fetchCategories,
    fetchKeywords,
    fetchRiskDistribution,
    fetchAll,
  }
})
