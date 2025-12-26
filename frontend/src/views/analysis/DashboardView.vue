<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, Row, Col, Statistic, Select, Spin } from 'ant-design-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useAnalysisStore } from '@/stores/analysis'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const analysisStore = useAnalysisStore()

const trendDays = ref(30)
const loading = computed(() => analysisStore.loading)

onMounted(async () => {
  await analysisStore.fetchAll()
})

async function handleTrendDaysChange() {
  await analysisStore.fetchTrend(trendDays.value)
}

// Trend Chart Options
const trendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
  },
  legend: {
    data: ['Rumors', 'Verified'],
    bottom: 0,
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
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
  },
  series: [
    {
      name: 'Rumors',
      type: 'line',
      data: analysisStore.trendData.map(d => d.rumors),
      smooth: true,
      lineStyle: { color: '#e53935' },
      itemStyle: { color: '#e53935' },
      areaStyle: { color: 'rgba(229, 57, 53, 0.1)' },
    },
    {
      name: 'Verified',
      type: 'line',
      data: analysisStore.trendData.map(d => d.verified),
      smooth: true,
      lineStyle: { color: '#2e7d32' },
      itemStyle: { color: '#2e7d32' },
      areaStyle: { color: 'rgba(46, 125, 50, 0.1)' },
    },
  ],
}))

// Category Pie Chart Options
const categoryOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
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
      avoidLabelOverlap: false,
      label: {
        show: false,
      },
      emphasis: {
        label: {
          show: true,
          fontWeight: 'bold',
        },
      },
      data: analysisStore.categories.map(c => ({
        name: c.category,
        value: c.count,
      })),
    },
  ],
}))

// Risk Distribution Bar Chart
const riskOption = computed(() => {
  const dist = analysisStore.riskDistribution
  return {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: ['Low', 'Medium', 'High', 'Critical'],
    },
    yAxis: {
      type: 'value',
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
      },
    ],
  }
})

// Word Cloud (simplified as bar chart for keywords)
const keywordsOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
  },
  xAxis: {
    type: 'value',
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
    right: '10%',
  },
  series: [
    {
      type: 'bar',
      data: analysisStore.keywords.slice(0, 10).map(k => k.count).reverse(),
      itemStyle: {
        color: '#1a1a1a',
      },
    },
  ],
}))
</script>

<template>
  <div class="dashboard-view">
    <header class="page-header">
      <h1 class="page-title">Analytics Dashboard</h1>
      <p class="page-subtitle">
        Visual insights into your rumor detection activities
      </p>
    </header>

    <Spin :spinning="loading">
      <!-- Stats Overview -->
      <Row :gutter="[24, 24]" class="stats-row">
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="Total Detections"
              :value="analysisStore.overview?.total_detections || 0"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="Rumors Detected"
              :value="analysisStore.overview?.total_rumors || 0"
              :value-style="{ color: 'var(--color-accent)' }"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="Verified Content"
              :value="analysisStore.overview?.total_verified || 0"
              :value-style="{ color: 'var(--color-success)' }"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card">
            <Statistic
              title="Avg Confidence"
              :value="((analysisStore.overview?.avg_confidence || 0) * 100).toFixed(1)"
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <!-- Charts Row 1 -->
      <Row :gutter="[24, 24]" class="charts-row">
        <Col :xs="24" :lg="16">
          <Card class="chart-card">
            <template #title>
              <div class="chart-header">
                <span>Detection Trend</span>
                <Select
                  v-model:value="trendDays"
                  style="width: 120px"
                  @change="handleTrendDaysChange"
                >
                  <Select.Option :value="7">Last 7 days</Select.Option>
                  <Select.Option :value="30">Last 30 days</Select.Option>
                  <Select.Option :value="90">Last 90 days</Select.Option>
                </Select>
              </div>
            </template>
            <VChart
              :option="trendOption"
              style="height: 300px"
              autoresize
            />
          </Card>
        </Col>
        <Col :xs="24" :lg="8">
          <Card class="chart-card" title="Category Distribution">
            <VChart
              :option="categoryOption"
              style="height: 300px"
              autoresize
            />
          </Card>
        </Col>
      </Row>

      <!-- Charts Row 2 -->
      <Row :gutter="[24, 24]" class="charts-row">
        <Col :xs="24" :lg="12">
          <Card class="chart-card" title="Risk Level Distribution">
            <VChart
              :option="riskOption"
              style="height: 300px"
              autoresize
            />
          </Card>
        </Col>
        <Col :xs="24" :lg="12">
          <Card class="chart-card" title="Top Keywords">
            <VChart
              :option="keywordsOption"
              style="height: 300px"
              autoresize
            />
          </Card>
        </Col>
      </Row>
    </Spin>
  </div>
</template>

<style scoped>
.dashboard-view {
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
</style>
