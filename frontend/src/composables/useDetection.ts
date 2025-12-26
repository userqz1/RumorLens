import { computed } from 'vue'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel } from '@/types'

export function useDetection() {
  const detectionStore = useDetectionStore()

  const currentDetection = computed(() => detectionStore.currentDetection)
  const loading = computed(() => detectionStore.loading)

  async function detectText(content: string) {
    return await detectionStore.detectSingle(content)
  }

  async function detectBatch(contents: string[]) {
    return await detectionStore.detectBatch(contents)
  }

  function getRiskColor(level: RiskLevel): string {
    const colors: Record<RiskLevel, string> = {
      low: 'var(--color-risk-low)',
      medium: 'var(--color-risk-medium)',
      high: 'var(--color-risk-high)',
      critical: 'var(--color-risk-critical)',
    }
    return colors[level]
  }

  function getRiskLabel(level: RiskLevel): string {
    const labels: Record<RiskLevel, string> = {
      low: 'LOW RISK',
      medium: 'MEDIUM RISK',
      high: 'HIGH RISK',
      critical: 'CRITICAL',
    }
    return labels[level]
  }

  function getConfidenceColor(confidence: number, isRumor: boolean): string {
    if (!isRumor) return 'var(--color-success)'
    return confidence < 0.4 ? 'var(--color-accent)' : 'var(--color-warning)'
  }

  return {
    currentDetection,
    loading,
    detectText,
    detectBatch,
    getRiskColor,
    getRiskLabel,
    getConfidenceColor,
  }
}
