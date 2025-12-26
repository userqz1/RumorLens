<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, Table, Tag, Button, Select, DatePicker, Space, Modal, message } from 'ant-design-vue'
import { DeleteOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel, Detection } from '@/types'
import dayjs from 'dayjs'

const detectionStore = useDetectionStore()

const selectedRowKeys = ref<string[]>([])
const filters = ref({
  is_rumor: undefined as boolean | undefined,
  risk_level: undefined as string | undefined,
  dateRange: [] as any[],
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
    title: 'Content',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true,
  },
  {
    title: 'Status',
    dataIndex: 'is_rumor',
    key: 'status',
    width: 120,
  },
  {
    title: 'Risk Level',
    dataIndex: 'risk_level',
    key: 'risk_level',
    width: 120,
  },
  {
    title: 'Confidence',
    dataIndex: 'confidence',
    key: 'confidence',
    width: 100,
  },
  {
    title: 'Date',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 100,
  },
]

onMounted(() => {
  fetchData()
})

async function fetchData(page = 1) {
  const params: any = { page }

  if (filters.value.is_rumor !== undefined) {
    params.is_rumor = filters.value.is_rumor
  }
  if (filters.value.risk_level) {
    params.risk_level = filters.value.risk_level
  }
  if (filters.value.dateRange?.length === 2) {
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
    dateRange: [],
  }
  fetchData(1)
}

async function handleDelete(id: string) {
  Modal.confirm({
    title: 'Delete Record',
    content: 'Are you sure you want to delete this record?',
    okText: 'Delete',
    okType: 'danger',
    async onOk() {
      try {
        await detectionStore.deleteDetection(id)
        message.success('Record deleted')
      } catch (e) {
        message.error('Failed to delete record')
      }
    },
  })
}

async function handleBatchDelete() {
  if (selectedRowKeys.value.length === 0) {
    message.warning('Please select records to delete')
    return
  }

  Modal.confirm({
    title: 'Delete Selected Records',
    content: `Are you sure you want to delete ${selectedRowKeys.value.length} records?`,
    okText: 'Delete',
    okType: 'danger',
    async onOk() {
      try {
        await detectionStore.deleteMultiple(selectedRowKeys.value)
        selectedRowKeys.value = []
        message.success('Records deleted')
      } catch (e) {
        message.error('Failed to delete records')
      }
    },
  })
}

function formatDate(dateStr: string) {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const rowSelection = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: string[]) => {
    selectedRowKeys.value = keys
  },
}
</script>

<template>
  <div class="history-view">
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">Detection History</h1>
        <p class="page-subtitle">
          View and manage your past rumor detection records
        </p>
      </div>
      <div class="header-actions">
        <Button :loading="loading" @click="() => fetchData()">
          <template #icon><ReloadOutlined /></template>
          Refresh
        </Button>
        <Button
          v-if="selectedRowKeys.length > 0"
          danger
          @click="handleBatchDelete"
        >
          <template #icon><DeleteOutlined /></template>
          Delete ({{ selectedRowKeys.length }})
        </Button>
      </div>
    </header>

    <!-- Filters -->
    <Card class="filters-card">
      <Space wrap>
        <Select
          v-model:value="filters.is_rumor"
          placeholder="Status"
          style="width: 140px"
          allow-clear
          @change="handleFilterChange"
        >
          <Select.Option :value="true">Rumor</Select.Option>
          <Select.Option :value="false">Verified</Select.Option>
        </Select>

        <Select
          v-model:value="filters.risk_level"
          placeholder="Risk Level"
          style="width: 140px"
          allow-clear
          @change="handleFilterChange"
        >
          <Select.Option value="low">Low</Select.Option>
          <Select.Option value="medium">Medium</Select.Option>
          <Select.Option value="high">High</Select.Option>
          <Select.Option value="critical">Critical</Select.Option>
        </Select>

        <DatePicker.RangePicker
          v-model:value="filters.dateRange"
          @change="handleFilterChange"
        />

        <Button @click="handleClearFilters">Clear Filters</Button>
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
          showTotal: (total: number) => `Total ${total} records`,
        }"
        row-key="id"
        @change="handleTableChange"
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
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <Space>
              <Button type="text" size="small" danger @click="handleDelete(record.id)">
                <template #icon><DeleteOutlined /></template>
              </Button>
            </Space>
          </template>
        </template>
      </Table>
    </Card>
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
</style>
