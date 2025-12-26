<script setup lang="ts">
import { ref } from 'vue'
import { Card, Upload, Button, Table, Tag, Progress, message } from 'ant-design-vue'
import { UploadOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel, Detection } from '@/types'

const detectionStore = useDetectionStore()

const textList = ref<string[]>([])
const results = ref<Detection[]>([])
const loading = ref(false)
const progress = ref(0)

const riskColors: Record<RiskLevel, string> = {
  low: 'success',
  medium: 'warning',
  high: 'orange',
  critical: 'error',
}

const columns = [
  {
    title: 'Content',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true,
    width: '40%',
  },
  {
    title: 'Status',
    dataIndex: 'is_rumor',
    key: 'status',
    width: '15%',
  },
  {
    title: 'Risk Level',
    dataIndex: 'risk_level',
    key: 'risk_level',
    width: '15%',
  },
  {
    title: 'Confidence',
    dataIndex: 'confidence',
    key: 'confidence',
    width: '15%',
  },
  {
    title: 'Category',
    key: 'category',
    width: '15%',
  },
]

function handleBeforeUpload(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    // Split by newlines, filter empty lines
    const lines = text.split('\n').filter(line => line.trim())
    textList.value = [...textList.value, ...lines]
    message.success(`Added ${lines.length} items from file`)
  }
  reader.readAsText(file)
  return false // Prevent default upload
}

function handleRemoveText(index: number) {
  textList.value.splice(index, 1)
}

function handleClearAll() {
  textList.value = []
  results.value = []
  progress.value = 0
}

async function handleDetect() {
  if (textList.value.length === 0) {
    message.warning('Please add texts to analyze')
    return
  }

  loading.value = true
  progress.value = 0
  results.value = []

  try {
    const result = await detectionStore.detectBatch(textList.value)
    results.value = result.results
    progress.value = 100
    message.success(`Analyzed ${result.success} of ${result.total} items`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'Batch detection failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="batch-detection-view">
    <header class="page-header">
      <h1 class="page-title">Batch Detection</h1>
      <p class="page-subtitle">
        Upload a file or add multiple texts for batch rumor analysis
      </p>
    </header>

    <div class="batch-grid">
      <!-- Input Section -->
      <Card class="input-card">
        <h3 class="card-title">Input Texts ({{ textList.length }} items)</h3>

        <Upload.Dragger
          :before-upload="handleBeforeUpload"
          :show-upload-list="false"
          accept=".txt,.csv"
          class="upload-dragger"
        >
          <p class="upload-icon"><UploadOutlined /></p>
          <p class="upload-text">Click or drag file to upload</p>
          <p class="upload-hint">Support .txt or .csv files (one text per line)</p>
        </Upload.Dragger>

        <!-- Text List Preview -->
        <div v-if="textList.length > 0" class="text-list">
          <div
            v-for="(text, index) in textList.slice(0, 10)"
            :key="index"
            class="text-item"
          >
            <span class="text-index">{{ index + 1 }}</span>
            <span class="text-content">{{ text }}</span>
            <Button
              type="text"
              size="small"
              danger
              @click="handleRemoveText(index)"
            >
              <template #icon><DeleteOutlined /></template>
            </Button>
          </div>
          <p v-if="textList.length > 10" class="text-more">
            ... and {{ textList.length - 10 }} more items
          </p>
        </div>

        <div class="input-actions">
          <Button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="textList.length === 0"
            @click="handleDetect"
          >
            Analyze All ({{ textList.length }})
          </Button>
          <Button size="large" @click="handleClearAll">
            Clear All
          </Button>
        </div>

        <!-- Progress -->
        <Progress
          v-if="loading || progress > 0"
          :percent="progress"
          :status="loading ? 'active' : 'success'"
          class="detection-progress"
        />
      </Card>

      <!-- Results Section -->
      <Card class="result-card">
        <h3 class="card-title">Results</h3>

        <Table
          :columns="columns"
          :data-source="results"
          :loading="loading"
          :pagination="{ pageSize: 10 }"
          row-key="id"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <Tag :color="record.is_rumor ? 'error' : 'success'">
                {{ record.is_rumor ? 'Rumor' : 'Verified' }}
              </Tag>
            </template>
            <template v-else-if="column.key === 'risk_level'">
              <Tag :color="riskColors[record.risk_level as RiskLevel]">
                {{ record.risk_level.toUpperCase() }}
              </Tag>
            </template>
            <template v-else-if="column.key === 'confidence'">
              {{ (record.confidence * 100).toFixed(1) }}%
            </template>
            <template v-else-if="column.key === 'category'">
              <Tag>{{ record.analysis?.category || 'N/A' }}</Tag>
            </template>
          </template>
        </Table>

        <!-- Summary Stats -->
        <div v-if="results.length > 0" class="results-summary">
          <div class="summary-item">
            <span class="summary-label">Total</span>
            <span class="summary-value">{{ results.length }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Rumors</span>
            <span class="summary-value text-error">
              {{ results.filter(r => r.is_rumor).length }}
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Verified</span>
            <span class="summary-value text-success">
              {{ results.filter(r => !r.is_rumor).length }}
            </span>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.batch-detection-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}

.page-subtitle {
  color: var(--color-text-muted);
}

.batch-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: var(--space-6);
}

.input-card,
.result-card {
  border: 1px solid var(--color-border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.upload-dragger {
  margin-bottom: var(--space-4);
}

.upload-icon {
  font-size: var(--text-3xl);
  color: var(--color-text-muted);
}

.upload-text {
  font-weight: var(--font-medium);
}

.upload-hint {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.text-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: var(--space-4);
  border: 1px solid var(--color-border);
}

.text-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.text-item:last-child {
  border-bottom: none;
}

.text-index {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  min-width: 24px;
}

.text-content {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--text-sm);
}

.text-more {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  font-style: italic;
}

.input-actions {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.detection-progress {
  margin-top: var(--space-4);
}

.results-summary {
  display: flex;
  gap: var(--space-8);
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.summary-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
}

@media (max-width: 1024px) {
  .batch-grid {
    grid-template-columns: 1fr;
  }
}
</style>
