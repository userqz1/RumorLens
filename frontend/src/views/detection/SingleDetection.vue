<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, Input, Button, Tag, Progress, Descriptions, message } from 'ant-design-vue'
import { SendOutlined, ClearOutlined } from '@ant-design/icons-vue'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel } from '@/types'

const detectionStore = useDetectionStore()

const inputText = ref('')
const loading = computed(() => detectionStore.loading)
const result = computed(() => detectionStore.currentDetection)

const riskColors: Record<RiskLevel, string> = {
  low: 'var(--color-risk-low)',
  medium: 'var(--color-risk-medium)',
  high: 'var(--color-risk-high)',
  critical: 'var(--color-risk-critical)',
}

const riskLabels: Record<RiskLevel, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '极高风险',
}

async function handleDetect() {
  if (!inputText.value.trim()) {
    message.warning('请输入要分析的文本')
    return
  }

  try {
    await detectionStore.detectSingle(inputText.value)
    message.success('检测完成')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '检测失败')
  }
}

function handleClear() {
  inputText.value = ''
  detectionStore.clearCurrent()
}
</script>

<template>
  <div class="detection-view">
    <header class="page-header">
      <h1 class="page-title">谣言检测</h1>
      <p class="page-subtitle">
        输入微博文本内容，使用AI进行谣言分析
      </p>
    </header>

    <div class="detection-grid">
      <!-- Input Section -->
      <Card class="input-card">
        <h3 class="card-title">输入文本</h3>
        <Input.TextArea
          v-model:value="inputText"
          :rows="10"
          placeholder="粘贴或输入要分析的微博内容..."
          :maxlength="5000"
          show-count
          class="input-textarea"
        />
        <div class="input-actions">
          <Button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!inputText.trim()"
            @click="handleDetect"
          >
            <template #icon><SendOutlined /></template>
            开始分析
          </Button>
          <Button size="large" @click="handleClear">
            <template #icon><ClearOutlined /></template>
            清空
          </Button>
        </div>
      </Card>

      <!-- Result Section -->
      <Card class="result-card" :loading="loading">
        <template v-if="result">
          <!-- Risk Indicator -->
          <div class="result-header">
            <div
              class="risk-badge"
              :style="{ backgroundColor: riskColors[result.risk_level] }"
            >
              {{ riskLabels[result.risk_level] }}
            </div>
            <div class="result-verdict">
              {{ result.is_rumor ? '疑似谣言' : '可能可信' }}
            </div>
          </div>

          <!-- Confidence Score -->
          <div class="confidence-section">
            <div class="confidence-label">可信度评分</div>
            <Progress
              :percent="Math.round(result.confidence * 100)"
              :stroke-color="result.is_rumor ? 'var(--color-accent)' : 'var(--color-success)'"
              :trail-color="'var(--color-border)'"
              :stroke-width="12"
            />
          </div>

          <!-- Explanation -->
          <div class="explanation-section">
            <h4 class="section-label">分析说明</h4>
            <p class="explanation-text">{{ result.explanation }}</p>
          </div>

          <!-- Analysis Details -->
          <template v-if="result.analysis">
            <Descriptions :column="1" class="analysis-details">
              <Descriptions.Item label="分类">
                <Tag>{{ result.analysis.category }}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="情感倾向">
                <Tag :color="result.analysis.sentiment === 'negative' ? 'error' : 'default'">
                  {{ result.analysis.sentiment === 'positive' ? '正面' : result.analysis.sentiment === 'negative' ? '负面' : '中性' }}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="关键词">
                <div class="keywords-list">
                  <Tag v-for="keyword in result.analysis.keywords" :key="keyword">
                    {{ keyword }}
                  </Tag>
                </div>
              </Descriptions.Item>
              <Descriptions.Item label="事实核查要点">
                <ul class="fact-list">
                  <li v-for="point in result.analysis.fact_check_points" :key="point">
                    {{ point }}
                  </li>
                </ul>
              </Descriptions.Item>
            </Descriptions>
          </template>
        </template>

        <template v-else>
          <div class="empty-state">
            <div class="empty-icon">?</div>
            <p class="empty-text">输入文本并点击分析查看结果</p>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.detection-view {
  max-width: 1200px;
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

.detection-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

.input-textarea {
  margin-bottom: var(--space-4);
}

.input-actions {
  display: flex;
  gap: var(--space-3);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.risk-badge {
  padding: var(--space-2) var(--space-4);
  color: white;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.result-verdict {
  font-family: var(--font-serif);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
}

.confidence-section {
  margin-bottom: var(--space-6);
}

.confidence-label {
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.explanation-section {
  margin-bottom: var(--space-6);
}

.section-label {
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.explanation-text {
  line-height: var(--leading-relaxed);
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.fact-list {
  margin: 0;
  padding-left: var(--space-4);
}

.fact-list li {
  margin-bottom: var(--space-1);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16) 0;
  color: var(--color-text-muted);
}

.empty-icon {
  font-family: var(--font-serif);
  font-size: 4rem;
  opacity: 0.3;
  margin-bottom: var(--space-4);
}

.empty-text {
  font-size: var(--text-lg);
}

@media (max-width: 768px) {
  .detection-grid {
    grid-template-columns: 1fr;
  }
}
</style>
