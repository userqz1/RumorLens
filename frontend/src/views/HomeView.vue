<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, Statistic, Button, Row, Col } from 'ant-design-vue'
import {
  SearchOutlined,
  FileAddOutlined,
  HistoryOutlined,
  DashboardOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'

const router = useRouter()
const analysisStore = useAnalysisStore()

const loading = ref(true)

onMounted(async () => {
  try {
    await analysisStore.fetchOverview()
  } finally {
    loading.value = false
  }
})

const quickActions = [
  {
    title: 'Single Detection',
    description: 'Analyze a single text for rumor detection',
    icon: SearchOutlined,
    path: '/detection',
    primary: true,
  },
  {
    title: 'Batch Detection',
    description: 'Upload and analyze multiple texts at once',
    icon: FileAddOutlined,
    path: '/detection/batch',
  },
  {
    title: 'History',
    description: 'View your past detection records',
    icon: HistoryOutlined,
    path: '/history',
  },
  {
    title: 'Dashboard',
    description: 'Visualize your detection analytics',
    icon: DashboardOutlined,
    path: '/dashboard',
  },
]
</script>

<template>
  <div class="home-view">
    <header class="home-header">
      <h1 class="home-title">Welcome to RumorLens</h1>
      <p class="home-subtitle">
        Your intelligent platform for Weibo rumor detection and analysis
      </p>
    </header>

    <!-- Stats Overview -->
    <section class="stats-section">
      <Row :gutter="24">
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card" :loading="loading">
            <Statistic
              title="Total Detections"
              :value="analysisStore.overview?.total_detections || 0"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card" :loading="loading">
            <Statistic
              title="Rumors Detected"
              :value="analysisStore.overview?.total_rumors || 0"
              :value-style="{ color: 'var(--color-accent)' }"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card" :loading="loading">
            <Statistic
              title="Verified Content"
              :value="analysisStore.overview?.total_verified || 0"
              :value-style="{ color: 'var(--color-success)' }"
            />
          </Card>
        </Col>
        <Col :xs="24" :sm="12" :lg="6">
          <Card class="stat-card" :loading="loading">
            <Statistic
              title="Rumor Rate"
              :value="((analysisStore.overview?.rumor_rate || 0) * 100).toFixed(1)"
              suffix="%"
              :prefix="analysisStore.overview?.rumor_rate > 0.5 ? ArrowUpOutlined : ArrowDownOutlined"
              :value-style="{
                color: analysisStore.overview?.rumor_rate > 0.5
                  ? 'var(--color-accent)'
                  : 'var(--color-success)'
              }"
            />
          </Card>
        </Col>
      </Row>
    </section>

    <!-- Quick Actions -->
    <section class="actions-section">
      <h2 class="section-title">Quick Actions</h2>
      <div class="actions-grid">
        <Card
          v-for="action in quickActions"
          :key="action.path"
          class="action-card hover-scale"
          :class="{ primary: action.primary }"
          @click="router.push(action.path)"
        >
          <div class="action-icon">
            <component :is="action.icon" />
          </div>
          <h3 class="action-title">{{ action.title }}</h3>
          <p class="action-description">{{ action.description }}</p>
        </Card>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}

.home-header {
  text-align: center;
  margin-bottom: var(--space-12);
}

.home-title {
  font-family: var(--font-serif);
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-4);
}

.home-subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-muted);
  max-width: 600px;
  margin: 0 auto;
}

.stats-section {
  margin-bottom: var(--space-12);
}

.stat-card {
  height: 100%;
  border: 1px solid var(--color-border);
  transition: box-shadow var(--transition-normal);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-6);
}

.action-card {
  cursor: pointer;
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
}

.action-card:hover {
  border-color: var(--color-text);
}

.action-card.primary {
  background-color: var(--color-text);
  color: var(--color-bg);
  border-color: var(--color-text);
}

.action-card.primary:hover {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
}

.action-icon {
  font-size: var(--text-3xl);
  margin-bottom: var(--space-4);
}

.action-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}

.action-description {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.action-card.primary .action-description {
  color: rgba(255, 255, 255, 0.7);
}
</style>
