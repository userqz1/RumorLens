import { computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

export function useChart() {
  const analysisStore = useAnalysisStore()

  const trendChartOption = computed(() => ({
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['Rumors', 'Verified'],
      bottom: 0,
      textStyle: {
        fontFamily: 'Instrument Sans, sans-serif',
      },
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
        fontFamily: 'Instrument Sans, sans-serif',
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
        lineStyle: { color: '#e53935', width: 2 },
        itemStyle: { color: '#e53935' },
        areaStyle: { color: 'rgba(229, 57, 53, 0.1)' },
      },
      {
        name: 'Verified',
        type: 'line',
        data: analysisStore.trendData.map(d => d.verified),
        smooth: true,
        lineStyle: { color: '#2e7d32', width: 2 },
        itemStyle: { color: '#2e7d32' },
        areaStyle: { color: 'rgba(46, 125, 50, 0.1)' },
      },
    ],
  }))

  const categoryPieOption = computed(() => ({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: {
        fontFamily: 'Instrument Sans, sans-serif',
      },
    },
    color: ['#1a1a1a', '#e53935', '#2e7d32', '#f9a825', '#666666', '#e5e5e5'],
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
            fontFamily: 'Instrument Sans, sans-serif',
          },
        },
        data: analysisStore.categories.map(c => ({
          name: c.category,
          value: c.count,
        })),
      },
    ],
  }))

  const riskBarOption = computed(() => {
    const dist = analysisStore.riskDistribution
    return {
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: ['Low', 'Medium', 'High', 'Critical'],
        axisLabel: {
          fontFamily: 'Instrument Sans, sans-serif',
        },
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

  const keywordsBarOption = computed(() => ({
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
        fontFamily: 'Instrument Sans, sans-serif',
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

  return {
    trendChartOption,
    categoryPieOption,
    riskBarOption,
    keywordsBarOption,
  }
}
