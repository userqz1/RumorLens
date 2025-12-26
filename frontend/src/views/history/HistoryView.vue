<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, Table, Tag, Button, Select, DatePicker, Space, Modal, Descriptions, message } from 'ant-design-vue'
import { DeleteOutlined, ReloadOutlined, EyeOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel, Detection } from '@/types'
import type { Dayjs } from 'dayjs'
import type { Key } from 'ant-design-vue/es/table/interface'
import dayjs from 'dayjs'

const detectionStore = useDetectionStore()

// 详情弹窗
const detailVisible = ref(false)
const currentDetail = ref<Detection | null>(null)

function showDetail(record: Detection) {
  currentDetail.value = record
  detailVisible.value = true
}

const selectedRowKeys = ref<string[]>([])
const filters = ref<{
  is_rumor: string | undefined
  risk_level: string | undefined
  dateRange: [Dayjs, Dayjs] | undefined
}>({
  is_rumor: undefined,
  risk_level: undefined,
  dateRange: undefined,
})

const loading = computed(() => detectionStore.loading)
const data = computed(() => detectionStore.detectionHistory)
const pagination = computed(() => detectionStore.historyPagination)

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
  },
  {
    title: '状态',
    dataIndex: 'is_rumor',
    key: 'status',
    width: 100,
  },
  {
    title: '风险',
    dataIndex: 'risk_level',
    key: 'risk_level',
    width: 100,
  },
  {
    title: '可信度',
    dataIndex: 'confidence',
    key: 'confidence',
    width: 90,
  },
  {
    title: '日期',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 130,
  },
]

onMounted(() => {
  fetchData()
})

async function fetchData(page = 1) {
  const params: any = { page }

  if (filters.value.is_rumor !== undefined) {
    params.is_rumor = filters.value.is_rumor === 'true'
  }
  if (filters.value.risk_level) {
    params.risk_level = filters.value.risk_level
  }
  if (filters.value.dateRange) {
    params.start_date = filters.value.dateRange[0].toISOString()
    params.end_date = filters.value.dateRange[1].toISOString()
  }

  await detectionStore.fetchHistory(params)
}

function handleTableChange(pag: any) {
  fetchData(pag.current)
}

function handleFilterChange() {
  fetchData(1)
}

function handleClearFilters() {
  filters.value = {
    is_rumor: undefined,
    risk_level: undefined,
    dateRange: undefined,
  }
  fetchData(1)
}

async function handleDelete(id: string) {
  Modal.confirm({
    title: '删除记录',
    content: '确定要删除这条记录吗？',
    okText: '删除',
    cancelText: '取消',
    okType: 'danger',
    async onOk() {
      try {
        await detectionStore.deleteDetection(id)
        message.success('删除成功')
      } catch (e) {
        message.error('删除失败')
      }
    },
  })
}

async function handleBatchDelete() {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的记录')
    return
  }

  Modal.confirm({
    title: '批量删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 条记录吗？`,
    okText: '删除',
    cancelText: '取消',
    okType: 'danger',
    async onOk() {
      try {
        await detectionStore.deleteMultiple(selectedRowKeys.value)
        selectedRowKeys.value = []
        message.success('删除成功')
      } catch (e) {
        message.error('删除失败')
      }
    },
  })
}

function formatDate(dateStr: string) {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

// 导出历史记录为CSV
function handleExport() {
  if (data.value.length === 0) {
    message.warning('暂无记录可导出')
    return
  }

  const headers = ['序号', '内容', '检测结果', '可信度', '风险等级', '分类', '情感', '检测时间', '分析说明']

  const rows = data.value.map((r, i) => {
    return [
      i + 1,
      `"${r.content.replace(/"/g, '""')}"`,
      r.is_rumor ? '谣言' : '可信',
      (r.confidence * 100).toFixed(1) + '%',
      r.risk_level === 'low' ? '低' : r.risk_level === 'medium' ? '中' : r.risk_level === 'high' ? '高' : '极高',
      r.analysis?.category || '未知',
      r.analysis?.sentiment === 'positive' ? '正面' : r.analysis?.sentiment === 'negative' ? '负面' : '中性',
      formatDate(r.created_at),
      `"${(r.explanation || '').replace(/"/g, '""')}"`
    ].join(',')
  })

  const csvContent = '\uFEFF' + headers.join(',') + '\n' + rows.join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `历史记录_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)

  message.success('导出成功')
}

const rowSelection = computed(() => ({
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: Key[]) => {
    selectedRowKeys.value = keys.map(k => String(k))
  },
}))
</script>

<template>
  <div class="history-view">
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">历史记录</h1>
        <p class="page-subtitle">
          查看和管理您的谣言检测记录
        </p>
      </div>
      <div class="header-actions">
        <Button :loading="loading" @click="() => fetchData()">
          <template #icon><ReloadOutlined /></template>
          刷新
        </Button>
        <Button
          v-if="data.length > 0"
          @click="handleExport"
        >
          <template #icon><DownloadOutlined /></template>
          导出CSV
        </Button>
        <Button
          v-if="selectedRowKeys.length > 0"
          danger
          @click="handleBatchDelete"
        >
          <template #icon><DeleteOutlined /></template>
          删除 ({{ selectedRowKeys.length }})
        </Button>
      </div>
    </header>

    <!-- Filters -->
    <Card class="filters-card">
      <Space wrap>
        <Select
          v-model:value="filters.is_rumor"
          placeholder="状态"
          style="width: 140px"
          allow-clear
          @change="handleFilterChange"
        >
          <Select.Option value="true">谣言</Select.Option>
          <Select.Option value="false">可信</Select.Option>
        </Select>

        <Select
          v-model:value="filters.risk_level"
          placeholder="风险等级"
          style="width: 140px"
          allow-clear
          @change="handleFilterChange"
        >
          <Select.Option value="low">低风险</Select.Option>
          <Select.Option value="medium">中风险</Select.Option>
          <Select.Option value="high">高风险</Select.Option>
          <Select.Option value="critical">极高风险</Select.Option>
        </Select>

        <DatePicker.RangePicker
          v-model:value="filters.dateRange"
          @change="handleFilterChange"
        />

        <Button @click="handleClearFilters">清除筛选</Button>
      </Space>
    </Card>

    <!-- Table -->
    <Card class="table-card">
      <Table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :row-selection="rowSelection"
        :pagination="{
          current: pagination.page,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: false,
          showTotal: (total: number) => `共 ${total} 条记录`,
        }"
        row-key="id"
        @change="handleTableChange"
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
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <Space>
              <Button type="link" size="small" @click="showDetail(record)">
                <template #icon><EyeOutlined /></template>
              </Button>
              <Button type="text" size="small" danger @click="handleDelete(record.id)">
                <template #icon><DeleteOutlined /></template>
              </Button>
            </Space>
          </template>
        </template>
      </Table>
    </Card>

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
          <Descriptions.Item label="检测时间">
            {{ formatDate(currentDetail.created_at) }}
          </Descriptions.Item>
        </Descriptions>
      </template>
    </Modal>
  </div>
</template>

<style scoped>
.history-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-6);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}

.page-subtitle {
  color: var(--color-text-muted);
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.filters-card {
  margin-bottom: var(--space-4);
  border: 1px solid var(--color-border);
}

.table-card {
  border: 1px solid var(--color-border);
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
</style>
