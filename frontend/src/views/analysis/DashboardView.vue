<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, Row, Col, Statistic, Select, Spin, Table, Tag, Modal, Descriptions, Empty } from 'ant-design-vue'
import { ReloadOutlined, InfoCircleOutlined } from '@ant-design/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useAnalysisStore } from '@/stores/analysis'
import { useDetectionStore } from '@/stores/detection'
import type { RiskLevel, Detection } from '@/types'
import dayjs from 'dayjs'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
])

const analysisStore = useAnalysisStore()
const detectionStore = useDetectionStore()

const trendDays = ref(30)
const loading = computed(() => analysisStore.loading)

// 详情弹窗
const detailVisible = ref(false)
const detailTitle = ref('')
const detailData = ref<any[]>([])

// 风险颜色
const riskColors: Record<RiskLevel, string> = {
  low: 'success',
  medium: 'warning',
  high: 'orange',
  critical: 'error',
}

onMounted(async () => {
  await Promise.all([
    analysisStore.fetchAll(),
    detectionStore.fetchHistory({ page: 1, page_size: 5 })
  ])
})

async function handleTrendDaysChange() {
  await analysisStore.fetchTrend(trendDays.value)
}

async function handleRefresh() {
  await Promise.all([
    analysisStore.fetchAll(),
    detectionStore.fetchHistory({ page: 1, page_size: 5 })
  ])
}

// 图表点击事件处理
function handleCategoryClick(params: any) {
  if (params.data) {
    detailTitle.value = `分类详情: ${params.data.name}`
    // 可以在这里加载该分类的详细数据
    detailData.value = [{ label: '分类', value: params.data.name }, { label: '数量', value: params.data.value }]
    detailVisible.value = true
  }
}

function handleRiskClick(params: any) {
  const riskLevels = ['低风险', '中风险', '高风险', '极高风险']
  const riskKeys = ['low', 'medium', 'high', 'critical']
  if (params.dataIndex !== undefined) {
    detailTitle.value = `风险等级详情: ${riskLevels[params.dataIndex]}`
    detailData.value = [
      { label: '风险等级', value: riskLevels[params.dataIndex] },
      { label: '检测数量', value: params.value }
    ]
    detailVisible.value = true
  }
}

function handleKeywordClick(params: any) {
  if (params.name) {
    detailTitle.value = `关键词详情: ${params.name}`
    detailData.value = [
      { label: '关键词', value: params.name },
      { label: '出现次数', value: params.value }
    ]
    detailVisible.value = true
  }
}

function formatDate(dateStr: string) {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

// 最近检测记录列
const recentColumns = [
  { title: '内容', dataIndex: 'content', key: 'content', ellipsis: true },
  { title: '状态', key: 'status', width: 80 },
  { title: '时间', key: 'time', width: 140 },
]

// Trend Chart Options - 增强版
const trendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e5e5e5',
    textStyle: { color: '#1a1a1a' },
    formatter: (params: any) => {
      let result = `<strong>${params[0].axisValue}</strong><br/>`
      params.forEach((item: any) => {
        result += `${item.marker} ${item.seriesName}: <strong>${item.value}</strong> 条<br/>`
      })
      return result
    }
  },
  legend: {
    data: ['谣言', '可信'],
    bottom: 0,
  },
  toolbox: {
    feature: {
      dataZoom: { yAxisIndex: 'none', title: { zoom: '缩放', back: '还原' } },
      restore: { title: '重置' },
      saveAsImage: { title: '保存图片' }
    },
    right: 20,
  },
  dataZoom: [
    { type: 'inside', start: 0, end: 100 },
    { type: 'slider', start: 0, end: 100, bottom: 30 }
  ],
  grid: {
    left: '3%',
    right: '4%',
    bottom: '20%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: analysisStore.trendData.map(d => d.date),
    axisLabel: {
      rotate: 45,
    },
  },
  yAxis: {
    type: 'value',
    name: '检测数',
  },
  series: [
    {
      name: '谣言',
      type: 'line',
      data: analysisStore.trendData.map(d => d.rumors),
      smooth: true,
      lineStyle: { color: '#e53935', width: 2 },
      itemStyle: { color: '#e53935' },
      areaStyle: { color: 'rgba(229, 57, 53, 0.1)' },
      emphasis: { focus: 'series' },
    },
    {
      name: '可信',
      type: 'line',
      data: analysisStore.trendData.map(d => d.verified),
      smooth: true,
      lineStyle: { color: '#2e7d32', width: 2 },
      itemStyle: { color: '#2e7d32' },
      areaStyle: { color: 'rgba(46, 125, 50, 0.1)' },
      emphasis: { focus: 'series' },
    },
  ],
}))

// Category Pie Chart Options - 增强版
const categoryOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e5e5e5',
    textStyle: { color: '#1a1a1a' },
    formatter: (params: any) => {
      return `<strong>${params.name}</strong><br/>数量: ${params.value} 条<br/>占比: ${params.percent}%`
    }
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
      },
      emphasis: {
        label: {
          show: true,
          fontWeight: 'bold',
          fontSize: 14,
        },
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        }
      },
      data: analysisStore.categories.map(c => ({
        name: c.category,
        value: c.count,
      })),
    },
  ],
}))

// Risk Distribution Bar Chart - 增强版
const riskOption = computed(() => {
  const dist = analysisStore.riskDistribution
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e5e5e5',
      textStyle: { color: '#1a1a1a' },
      formatter: (params: any) => {
        const item = params[0]
        return `<strong>${item.name}风险</strong><br/>检测数量: ${item.value} 条`
      }
    },
    xAxis: {
      type: 'category',
      data: ['低', '中', '高', '极高'],
      axisLabel: {
        fontWeight: 'bold'
      }
    },
    yAxis: {
      type: 'value',
      name: '检测数',
    },
    series: [
      {
        type: 'bar',
        data: [
          { value: dist?.low || 0, itemStyle: { color: '#2e7d32' } },
          { value: dist?.medium || 0, itemStyle: { color: '#f9a825' } },
          { value: dist?.high || 0, itemStyle: { color: '#ef6c00' } },
          { value: dist?.critical || 0, itemStyle: { color: '#c62828' } },
        ],
        barWidth: '50%',
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.2)'
          }
        },
        label: {
          show: true,
          position: 'top',
          fontWeight: 'bold'
        }
      },
    ],
  }
})

// Keywords Bar Chart - 增强版
const keywordsOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e5e5e5',
    textStyle: { color: '#1a1a1a' },
    formatter: (params: any) => {
      const item = params[0]
      return `<strong>${item.name}</strong><br/>出现次数: ${item.value} 次`
    }
  },
  xAxis: {
    type: 'value',
    name: '次数',
  },
  yAxis: {
    type: 'category',
    data: analysisStore.keywords.slice(0, 10).map(k => k.keyword).reverse(),
    axisLabel: {
      width: 80,
      overflow: 'truncate',
    },
  },
  grid: {
    left: '25%',
    right: '15%',
  },
  series: [
    {
      type: 'bar',
      data: analysisStore.keywords.slice(0, 10).map(k => k.count).reverse(),
      itemStyle: {
        color: '#1a1a1a',
        borderRadius: [0, 4, 4, 0]
      },
      emphasis: {
        itemStyle: {
          color: '#333'
        }
      },
      label: {
        show: true,
        position: 'right',
        fontWeight: 'bold'
      }
    },
  ],
}))
</script>

<template>
  <div class="dashboard-view">
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">
          可视化展示您的谣言检测数据，点击图表可查看详情
        </p>
      </div>
      <div class="header-actions">
        <Select
          v-model:value="trendDays"
          style="width: 120px"
          @change="handleTrendDaysChange"
        >
          <Select.Option :value="7">近7天</Select.Option>
          <Select.Option :value="30">近30天</Select.Option>
          <Select.Option :value="90">近90天</Select.Option>
        </Select>
        <a-button :loading="loading" @click="handleRefresh">
          <template #icon><ReloadOutlined /></template>
          刷新数据
        </a-button>
      </div>
    </header>

    <Spin :spinning="loading">
      <!-- Stats Overview -->
      <Row :gutter="[24, 24]" class="stats-row">
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="检测总数"
              :value="analysisStore.overview?.total_detections || 0"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="检出谣言"
              :value="analysisStore.overview?.total_rumors || 0"
              :value-style="{ color: 'var(--color-accent)' }"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="可信内容"
              :value="analysisStore.overview?.total_verified || 0"
              :value-style="{ color: 'var(--color-success)' }"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="平均可信度"
              :value="((analysisStore.overview?.avg_confidence || 0) * 100).toFixed(1)"
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <!-- Charts Row 1 -->
      <Row :gutter="[24, 24]" class="charts-row">
        <Col :xs="24" :lg="16">
          <Card class="chart-card" title="检测趋势">
            <template #extra>
              <span class="chart-tip">
                <InfoCircleOutlined /> 可拖拽缩放
              </span>
            </template>
            <VChart
              :option="trendOption"
              style="height: 350px"
              autoresize
            />
          </Card>
        </Col>
        <Col :xs="24" :lg="8">
          <Card class="chart-card" title="分类分布">
            <template #extra>
              <span class="chart-tip">
                <InfoCircleOutlined /> 点击查看详情
              </span>
            </template>
            <VChart
              :option="categoryOption"
              style="height: 350px"
              autoresize
              @click="handleCategoryClick"
            />
          </Card>
        </Col>
      </Row>

      <!-- Charts Row 2 -->
      <Row :gutter="[24, 24]" class="charts-row">
        <Col :xs="24" :lg="12">
          <Card class="chart-card" title="风险等级分布">
            <VChart
              :option="riskOption"
              style="height: 300px"
              autoresize
              @click="handleRiskClick"
            />
          </Card>
        </Col>
        <Col :xs="24" :lg="12">
          <Card class="chart-card" title="热门关键词 TOP 10">
            <VChart
              :option="keywordsOption"
              style="height: 300px"
              autoresize
              @click="handleKeywordClick"
            />
          </Card>
        </Col>
      </Row>

      <!-- Recent Detections -->
      <Row :gutter="[24, 24]" class="charts-row">
        <Col :xs="24">
          <Card class="chart-card" title="最近检测记录">
            <template #extra>
              <router-link to="/history" class="view-all-link">查看全部</router-link>
            </template>
            <Table
              v-if="detectionStore.detectionHistory.length > 0"
              :columns="recentColumns"
              :data-source="detectionStore.detectionHistory.slice(0, 5)"
              :pagination="false"
              row-key="id"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'status'">
                  <Tag :color="record.is_rumor ? 'error' : 'success'">
                    {{ record.is_rumor ? '谣言' : '可信' }}
                  </Tag>
                </template>
                <template v-else-if="column.key === 'time'">
                  {{ formatDate(record.created_at) }}
                </template>
              </template>
            </Table>
            <Empty v-else description="暂无检测记录" />
          </Card>
        </Col>
      </Row>
    </Spin>

    <!-- 详情弹窗 -->
    <Modal
      v-model:open="detailVisible"
      :title="detailTitle"
      :footer="null"
      width="400px"
    >
      <Descriptions :column="1" bordered size="small">
        <Descriptions.Item
          v-for="item in detailData"
          :key="item.label"
          :label="item.label"
        >
          {{ item.value }}
        </Descriptions.Item>
      </Descriptions>
    </Modal>
  </div>
</template>

<style scoped>
.dashboard-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-8);
}

.header-content {
  flex: 1;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}

.page-subtitle {
  color: var(--color-text-muted);
}

.stats-row {
  margin-bottom: var(--space-6);
}

.stat-card {
  height: 100%;
  border: 1px solid var(--color-border);
}

.charts-row {
  margin-bottom: var(--space-6);
}

.chart-card {
  border: 1px solid var(--color-border);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-tip {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.view-all-link {
  font-size: var(--text-sm);
  color: var(--color-text);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.view-all-link:hover {
  color: var(--color-accent);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-4);
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
