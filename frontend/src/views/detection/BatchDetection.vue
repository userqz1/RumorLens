<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, Upload, Button, Table, Tag, Progress, InputNumber, Modal, Descriptions, Statistic, message } from 'ant-design-vue'
import { UploadOutlined, EyeOutlined, DownloadOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel, Detection } from '@/types'

const detectionStore = useDetectionStore()

const textList = ref<string[]>([])
const originalLabels = ref<boolean[]>([])  // 原始标签（如果CSV包含label列）
const hasLabels = ref(false)  // 是否有原始标签
const results = ref<Detection[]>([])
const loading = ref(false)
const progress = ref(0)

// 详情弹窗
const detailVisible = ref(false)
const currentDetail = ref<Detection | null>(null)

function showDetail(record: Detection) {
  currentDetail.value = record
  detailVisible.value = true
}

// 范围选择
const startIndex = ref(1)
const endIndex = ref(100)

// 计算实际要检测的文本数量
const selectedCount = computed(() => {
  if (textList.value.length === 0) return 0
  const start = Math.max(1, startIndex.value)
  const end = Math.min(textList.value.length, endIndex.value)
  return Math.max(0, end - start + 1)
})

// 获取选中范围的文本
const selectedTexts = computed(() => {
  if (textList.value.length === 0) return []
  const start = Math.max(0, startIndex.value - 1)
  const end = Math.min(textList.value.length, endIndex.value)
  return textList.value.slice(start, end)
})

// 获取选中范围的原始标签
const selectedLabels = computed(() => {
  if (!hasLabels.value || originalLabels.value.length === 0) return []
  const start = Math.max(0, startIndex.value - 1)
  const end = Math.min(originalLabels.value.length, endIndex.value)
  return originalLabels.value.slice(start, end)
})

// 准确率统计
const accuracyStats = computed(() => {
  if (!hasLabels.value || results.value.length === 0 || selectedLabels.value.length === 0) {
    return null
  }

  let correct = 0
  let total = Math.min(results.value.length, selectedLabels.value.length)

  for (let i = 0; i < total; i++) {
    const predicted = results.value[i].is_rumor
    const actual = selectedLabels.value[i]
    if (predicted === actual) {
      correct++
    }
  }

  // 计算 TP, TN, FP, FN
  let tp = 0, tn = 0, fp = 0, fn = 0
  for (let i = 0; i < total; i++) {
    const predicted = results.value[i].is_rumor
    const actual = selectedLabels.value[i]
    if (predicted && actual) tp++
    else if (!predicted && !actual) tn++
    else if (predicted && !actual) fp++
    else fn++
  }

  const accuracy = total > 0 ? (correct / total * 100) : 0
  const precision = (tp + fp) > 0 ? (tp / (tp + fp) * 100) : 0
  const recall = (tp + fn) > 0 ? (tp / (tp + fn) * 100) : 0
  const f1 = (precision + recall) > 0 ? (2 * precision * recall / (precision + recall)) : 0

  return {
    total,
    correct,
    accuracy: accuracy.toFixed(1),
    precision: precision.toFixed(1),
    recall: recall.toFixed(1),
    f1: f1.toFixed(1),
    tp, tn, fp, fn
  }
})

const riskColors: Record<RiskLevel, string> = {
  low: 'success',
  medium: 'warning',
  high: 'orange',
  critical: 'error',
}

const columns = [
  {
    title: '内容',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true,
    width: '35%',
  },
  {
    title: '状态',
    dataIndex: 'is_rumor',
    key: 'status',
    width: '10%',
  },
  {
    title: '风险',
    dataIndex: 'risk_level',
    key: 'risk_level',
    width: '10%',
  },
  {
    title: '可信度',
    dataIndex: 'confidence',
    key: 'confidence',
    width: '10%',
  },
  {
    title: '分类',
    key: 'category',
    width: '10%',
  },
  {
    title: '操作',
    key: 'actions',
    width: '10%',
  },
]

function parseCSV(text: string): { texts: string[], labels: boolean[] } {
  const lines = text.split('\n').filter(line => line.trim())
  if (lines.length === 0) return { texts: [], labels: [] }

  // Check if first line looks like a header (contains common column names)
  const firstLine = lines[0].toLowerCase()
  const hasHeader = firstLine.includes('text') || firstLine.includes('content') ||
                    firstLine.includes('event_id') || firstLine.includes('label')

  if (!hasHeader) {
    // Not a CSV with headers, treat as plain text
    return { texts: lines, labels: [] }
  }

  // Parse header to find text and label column index
  const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
  let textIndex = headers.findIndex(h => h === 'text')
  if (textIndex === -1) {
    textIndex = headers.findIndex(h => h === 'content')
  }
  if (textIndex === -1) {
    textIndex = headers.findIndex(h => h === 'original_text')
  }

  // Find label column (is_rumor, label, rumor, etc.)
  let labelIndex = headers.findIndex(h => h === 'label')
  if (labelIndex === -1) {
    labelIndex = headers.findIndex(h => h === 'is_rumor')
  }
  if (labelIndex === -1) {
    labelIndex = headers.findIndex(h => h === 'rumor')
  }

  if (textIndex === -1) {
    message.warning('CSV文件中未找到 text/content 列，将按普通文本处理')
    return { texts: lines.slice(1), labels: [] }
  }

  // Extract text and label columns from each row
  const texts: string[] = []
  const labels: boolean[] = []

  for (let i = 1; i < lines.length; i++) {
    const row = lines[i]
    // Simple CSV parsing (handles basic cases)
    const columns = row.split(',')
    if (columns[textIndex]) {
      const cellText = columns[textIndex].trim().replace(/^["']|["']$/g, '')
      if (cellText) {
        texts.push(cellText)

        // Parse label if exists
        if (labelIndex !== -1 && columns[labelIndex]) {
          const labelValue = columns[labelIndex].trim().toLowerCase()
          // 支持多种标签格式: 1/0, true/false, 是/否, rumor/not_rumor
          const isRumor = labelValue === '1' || labelValue === 'true' ||
                          labelValue === '是' || labelValue === 'rumor' ||
                          labelValue === 'yes'
          labels.push(isRumor)
        }
      }
    }
  }

  return { texts, labels }
}

function handleBeforeUpload(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    const isCSV = file.name.toLowerCase().endsWith('.csv')

    let extractedTexts: string[]
    let extractedLabels: boolean[] = []

    if (isCSV) {
      const parsed = parseCSV(text)
      extractedTexts = parsed.texts
      extractedLabels = parsed.labels

      if (extractedLabels.length > 0) {
        message.success(`已从CSV文件解析 ${extractedTexts.length} 条文本（含标签列，可对比准确率）`)
        hasLabels.value = true
        originalLabels.value = extractedLabels
      } else {
        message.success(`已从CSV文件解析 ${extractedTexts.length} 条文本`)
        hasLabels.value = false
        originalLabels.value = []
      }
    } else {
      // Plain text file - split by newlines
      extractedTexts = text.split('\n').filter(line => line.trim())
      message.success(`已添加 ${extractedTexts.length} 条文本`)
      hasLabels.value = false
      originalLabels.value = []
    }

    textList.value = extractedTexts
    // 重置范围选择
    startIndex.value = 1
    endIndex.value = Math.min(100, extractedTexts.length) // 默认选择前100条
    // 清空之前的结果
    results.value = []
    progress.value = 0
  }
  reader.readAsText(file)
  return false // Prevent default upload
}

function handleRemoveText(index: number) {
  textList.value.splice(index, 1)
}

function handleClearAll() {
  textList.value = []
  originalLabels.value = []
  hasLabels.value = false
  results.value = []
  progress.value = 0
  startIndex.value = 1
  endIndex.value = 100
}

// 导出结果为CSV
function handleExport() {
  if (results.value.length === 0) {
    message.warning('暂无检测结果可导出')
    return
  }

  const headers = ['序号', '内容', 'AI检测结果', '可信度', '风险等级', '分类', '情感', '分析说明']
  if (hasLabels.value) {
    headers.push('原始标签', '是否一致')
  }

  const rows = results.value.map((r, i) => {
    const row = [
      i + 1,
      `"${r.content.replace(/"/g, '""')}"`,  // 处理CSV中的双引号
      r.is_rumor ? '谣言' : '可信',
      (r.confidence * 100).toFixed(1) + '%',
      r.risk_level === 'low' ? '低' : r.risk_level === 'medium' ? '中' : r.risk_level === 'high' ? '高' : '极高',
      r.analysis?.category || '未知',
      r.analysis?.sentiment === 'positive' ? '正面' : r.analysis?.sentiment === 'negative' ? '负面' : '中性',
      `"${(r.explanation || '').replace(/"/g, '""')}"`
    ]

    if (hasLabels.value && selectedLabels.value[i] !== undefined) {
      const actualLabel = selectedLabels.value[i]
      row.push(actualLabel ? '谣言' : '可信')
      row.push(r.is_rumor === actualLabel ? '一致' : '不一致')
    }

    return row.join(',')
  })

  const csvContent = '\uFEFF' + headers.join(',') + '\n' + rows.join('\n')  // 添加BOM支持中文
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `检测结果_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)

  message.success('导出成功')
}

async function handleDetect() {
  if (selectedTexts.value.length === 0) {
    message.warning('请添加要分析的文本或调整检测范围')
    return
  }

  loading.value = true
  progress.value = 0
  results.value = []

  const BATCH_SIZE = 20 // 每批处理20条（一次API调用分析多条）
  const textsToDetect = selectedTexts.value
  const totalItems = textsToDetect.length
  let successCount = 0
  let failedCount = 0

  try {
    // 分批处理
    for (let i = 0; i < totalItems; i += BATCH_SIZE) {
      const batch = textsToDetect.slice(i, i + BATCH_SIZE)
      const batchNum = Math.floor(i / BATCH_SIZE) + 1
      const totalBatches = Math.ceil(totalItems / BATCH_SIZE)

      try {
        const result = await detectionStore.detectBatch(batch)
        results.value = [...results.value, ...result.results]
        successCount += result.success
        failedCount += result.failed
      } catch (error: any) {
        console.error(`批次 ${batchNum} 失败:`, error)
        failedCount += batch.length
      }

      // 更新进度
      progress.value = Math.round(((i + batch.length) / totalItems) * 100)

      // 如果还有更多批次，稍微延迟以避免请求过快
      if (i + BATCH_SIZE < totalItems) {
        await new Promise(resolve => setTimeout(resolve, 300))
      }
    }

    // 确保结果已经渲染后再显示完成消息
    await new Promise(resolve => setTimeout(resolve, 100))
    progress.value = 100
    message.success(`检测完成！成功 ${successCount} 条，失败 ${failedCount} 条`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量检测失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="batch-detection-view">
    <header class="page-header">
      <h1 class="page-title">批量检测</h1>
      <p class="page-subtitle">
        上传数据集文件，选择范围进行批量检测（每20条一次AI分析，大幅提升效率）
      </p>
    </header>

    <div class="batch-grid">
      <!-- Input Section -->
      <Card class="input-card">
        <h3 class="card-title">数据文件 (共 {{ textList.length }} 条)</h3>

        <Upload.Dragger
          :before-upload="handleBeforeUpload"
          :show-upload-list="false"
          accept=".txt,.csv"
          class="upload-dragger"
        >
          <p class="upload-icon"><UploadOutlined /></p>
          <p class="upload-text">点击或拖拽文件上传</p>
          <p class="upload-hint">支持 .txt 文件或含 text 列的 .csv 数据集文件</p>
        </Upload.Dragger>

        <!-- Range Selector -->
        <div v-if="textList.length > 0" class="range-selector">
          <h4 class="range-title">选择检测范围</h4>
          <div class="range-inputs">
            <div class="range-input-group">
              <span class="range-label">从第</span>
              <InputNumber
                v-model:value="startIndex"
                :min="1"
                :max="textList.length"
                size="small"
              />
              <span class="range-label">条</span>
            </div>
            <div class="range-input-group">
              <span class="range-label">到第</span>
              <InputNumber
                v-model:value="endIndex"
                :min="1"
                :max="textList.length"
                size="small"
              />
              <span class="range-label">条</span>
            </div>
          </div>
          <p class="range-info">
            将检测 <strong>{{ selectedCount }}</strong> 条数据
          </p>
        </div>

        <!-- Text List Preview - 可滚动查看所有选中内容 -->
        <div v-if="selectedTexts.length > 0" class="text-list">
          <div
            v-for="(text, index) in selectedTexts"
            :key="index"
            class="text-item"
            :title="text"
          >
            <span class="text-index">{{ startIndex + index }}</span>
            <span class="text-content">{{ text }}</span>
          </div>
        </div>

        <div class="input-actions">
          <Button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="selectedCount === 0"
            @click="handleDetect"
          >
            开始分析 ({{ selectedCount }} 条)
          </Button>
          <Button size="large" @click="handleClearAll">
            清空全部
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
        <div class="result-header">
          <h3 class="card-title">检测结果</h3>
          <Button
            v-if="results.length > 0"
            type="primary"
            @click="handleExport"
          >
            <template #icon><DownloadOutlined /></template>
            导出CSV
          </Button>
        </div>

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
                {{ record.is_rumor ? '谣言' : '可信' }}
              </Tag>
            </template>
            <template v-else-if="column.key === 'risk_level'">
              <Tag :color="riskColors[record.risk_level as RiskLevel]">
                {{ record.risk_level === 'low' ? '低' : record.risk_level === 'medium' ? '中' : record.risk_level === 'high' ? '高' : '极高' }}
              </Tag>
            </template>
            <template v-else-if="column.key === 'confidence'">
              {{ (record.confidence * 100).toFixed(1) }}%
            </template>
            <template v-else-if="column.key === 'category'">
              <Tag>{{ record.analysis?.category || '未知' }}</Tag>
            </template>
            <template v-else-if="column.key === 'actions'">
              <Button type="link" size="small" @click="showDetail(record)">
                <template #icon><EyeOutlined /></template>
                详情
              </Button>
            </template>
          </template>
        </Table>

        <!-- Summary Stats -->
        <div v-if="results.length > 0" class="results-summary">
          <div class="summary-item">
            <span class="summary-label">总数</span>
            <span class="summary-value">{{ results.length }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">谣言</span>
            <span class="summary-value text-error">
              {{ results.filter(r => r.is_rumor).length }}
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">可信</span>
            <span class="summary-value text-success">
              {{ results.filter(r => !r.is_rumor).length }}
            </span>
          </div>
        </div>

        <!-- Accuracy Stats (when labels available) -->
        <div v-if="accuracyStats" class="accuracy-section">
          <h4 class="accuracy-title">与数据集标签对比</h4>
          <div class="accuracy-grid">
            <div class="accuracy-item accuracy-main">
              <Statistic
                title="准确率"
                :value="accuracyStats.accuracy"
                suffix="%"
                :value-style="{ color: parseFloat(accuracyStats.accuracy) >= 70 ? '#2e7d32' : parseFloat(accuracyStats.accuracy) >= 50 ? '#f9a825' : '#e53935' }"
              />
              <span class="accuracy-detail">{{ accuracyStats.correct }}/{{ accuracyStats.total }}</span>
            </div>
            <div class="accuracy-item">
              <Statistic title="精确率" :value="accuracyStats.precision" suffix="%" />
            </div>
            <div class="accuracy-item">
              <Statistic title="召回率" :value="accuracyStats.recall" suffix="%" />
            </div>
            <div class="accuracy-item">
              <Statistic title="F1分数" :value="accuracyStats.f1" suffix="%" />
            </div>
          </div>
          <div class="confusion-matrix">
            <div class="matrix-row">
              <span class="matrix-label">真阳性 (TP)</span>
              <Tag color="success">{{ accuracyStats.tp }}</Tag>
            </div>
            <div class="matrix-row">
              <span class="matrix-label">真阴性 (TN)</span>
              <Tag color="success">{{ accuracyStats.tn }}</Tag>
            </div>
            <div class="matrix-row">
              <span class="matrix-label">假阳性 (FP)</span>
              <Tag color="error">{{ accuracyStats.fp }}</Tag>
            </div>
            <div class="matrix-row">
              <span class="matrix-label">假阴性 (FN)</span>
              <Tag color="error">{{ accuracyStats.fn }}</Tag>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- 详情弹窗 -->
    <Modal
      v-model:open="detailVisible"
      title="检测详情"
      width="700px"
      :footer="null"
    >
      <template v-if="currentDetail">
        <div class="detail-header">
          <Tag :color="currentDetail.is_rumor ? 'error' : 'success'" class="detail-tag">
            {{ currentDetail.is_rumor ? '疑似谣言' : '可能可信' }}
          </Tag>
          <Tag :color="riskColors[currentDetail.risk_level as RiskLevel]" class="detail-tag">
            {{ currentDetail.risk_level === 'low' ? '低风险' : currentDetail.risk_level === 'medium' ? '中风险' : currentDetail.risk_level === 'high' ? '高风险' : '极高风险' }}
          </Tag>
          <span class="detail-confidence">可信度: {{ (currentDetail.confidence * 100).toFixed(1) }}%</span>
        </div>

        <Descriptions :column="1" bordered size="small" class="detail-descriptions">
          <Descriptions.Item label="原文内容">
            <div class="detail-content">{{ currentDetail.content }}</div>
          </Descriptions.Item>
          <Descriptions.Item label="分析说明">
            {{ currentDetail.explanation || '暂无' }}
          </Descriptions.Item>
          <Descriptions.Item label="分类">
            <Tag>{{ currentDetail.analysis?.category || '未知' }}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="情感倾向">
            <Tag :color="currentDetail.analysis?.sentiment === 'negative' ? 'error' : currentDetail.analysis?.sentiment === 'positive' ? 'success' : 'default'">
              {{ currentDetail.analysis?.sentiment === 'positive' ? '正面' : currentDetail.analysis?.sentiment === 'negative' ? '负面' : '中性' }}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="关键词">
            <div class="detail-keywords">
              <Tag v-for="keyword in (currentDetail.analysis?.keywords || [])" :key="keyword">
                {{ keyword }}
              </Tag>
              <span v-if="!currentDetail.analysis?.keywords?.length" class="no-data">暂无</span>
            </div>
          </Descriptions.Item>
        </Descriptions>
      </template>
    </Modal>
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

.range-selector {
  margin-bottom: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
}

.range-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.range-inputs {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-2);
}

.range-input-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.range-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.range-info {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.range-info strong {
  color: var(--color-text);
  font-weight: var(--font-bold);
}

.text-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: var(--space-4);
  border: 1px solid var(--color-border);
}

.text-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background-color 0.2s;
}

.text-item:hover {
  background-color: var(--color-bg);
}

.text-item:last-child {
  border-bottom: none;
}

.text-index {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  min-width: 32px;
  flex-shrink: 0;
}

.text-content {
  flex: 1;
  font-size: var(--text-sm);
  line-height: 1.5;
  word-break: break-all;
  /* 默认显示2行，悬停显示全部 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.text-item:hover .text-content {
  -webkit-line-clamp: unset;
  overflow: visible;
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

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.detail-tag {
  font-size: var(--text-sm);
}

.detail-confidence {
  margin-left: auto;
  font-weight: var(--font-semibold);
}

.detail-descriptions {
  margin-top: var(--space-4);
}

.detail-content {
  max-height: 150px;
  overflow-y: auto;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.detail-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.no-data {
  color: var(--color-text-muted);
  font-style: italic;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.result-header .card-title {
  margin-bottom: 0;
}

/* Accuracy Stats */
.accuracy-section {
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}

.accuracy-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.accuracy-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.accuracy-item {
  text-align: center;
  padding: var(--space-3);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
}

.accuracy-main {
  position: relative;
}

.accuracy-detail {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  display: block;
  margin-top: var(--space-1);
}

.confusion-matrix {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.matrix-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.matrix-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

@media (max-width: 1024px) {
  .batch-grid {
    grid-template-columns: 1fr;
  }

  .accuracy-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
