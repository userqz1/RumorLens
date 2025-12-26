import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Detection } from '@/types'
import { detectionApi, type HistoryFilters } from '@/api/detection'

export const useDetectionStore = defineStore('detection', () => {
  // State
  const currentDetection = ref<Detection | null>(null)
  const detectionHistory = ref<Detection[]>([])
  const historyPagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0,
  })
  const loading = ref(false)
  const detectingContent = ref('')

  // Actions
  async function detectSingle(content: string, includeAnalysis = true) {
    loading.value = true
    detectingContent.value = content
    try {
      currentDetection.value = await detectionApi.detectSingle({
        content,
        include_analysis: includeAnalysis,
      })
      return currentDetection.value
    } finally {
      loading.value = false
      detectingContent.value = ''
    }
  }

  async function detectBatch(contents: string[], includeAnalysis = true) {
    loading.value = true
    try {
      const result = await detectionApi.detectBatch({
        contents,
        include_analysis: includeAnalysis,
      })
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(filters: HistoryFilters = {}) {
    loading.value = true
    try {
      const result = await detectionApi.getHistory({
        page: filters.page || historyPagination.value.page,
        page_size: filters.page_size || historyPagination.value.pageSize,
        ...filters,
      })
      detectionHistory.value = result.items
      historyPagination.value = {
        total: result.total,
        page: result.page,
        pageSize: result.page_size,
        totalPages: result.total_pages,
      }
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchDetection(id: string) {
    loading.value = true
    try {
      currentDetection.value = await detectionApi.getDetection(id)
      return currentDetection.value
    } finally {
      loading.value = false
    }
  }

  async function deleteDetection(id: string) {
    await detectionApi.deleteDetection(id)
    detectionHistory.value = detectionHistory.value.filter(d => d.id !== id)
    if (currentDetection.value?.id === id) {
      currentDetection.value = null
    }
  }

  async function deleteMultiple(ids: string[]) {
    await detectionApi.deleteMultiple(ids)
    detectionHistory.value = detectionHistory.value.filter(d => !ids.includes(d.id))
  }

  function clearCurrent() {
    currentDetection.value = null
  }

  return {
    // State
    currentDetection,
    detectionHistory,
    historyPagination,
    loading,
    detectingContent,
    // Actions
    detectSingle,
    detectBatch,
    fetchHistory,
    fetchDetection,
    deleteDetection,
    deleteMultiple,
    clearCurrent,
  }
})
