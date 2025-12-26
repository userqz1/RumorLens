<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { Layout, Menu, Button, Dropdown, Avatar } from 'ant-design-vue'
import {
  HomeOutlined,
  SearchOutlined,
  HistoryOutlined,
  DashboardOutlined,
  UserOutlined,
  LogoutOutlined,
  FileAddOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'

const { Header, Sider, Content } = Layout

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const collapsed = ref(false)

const selectedKeys = computed(() => {
  const path = route.path
  if (path === '/') return ['home']
  if (path === '/detection') return ['detection']
  if (path === '/detection/batch') return ['batch']
  if (path === '/history') return ['history']
  if (path === '/dashboard') return ['dashboard']
  if (path === '/settings') return ['settings']
  return []
})

const menuItems = [
  { key: 'home', icon: HomeOutlined, label: '首页', path: '/' },
  { key: 'detection', icon: SearchOutlined, label: '谣言检测', path: '/detection' },
  { key: 'batch', icon: FileAddOutlined, label: '批量检测', path: '/detection/batch' },
  { key: 'history', icon: HistoryOutlined, label: '历史记录', path: '/history' },
  { key: 'dashboard', icon: DashboardOutlined, label: '数据分析', path: '/dashboard' },
]

function handleMenuClick({ key }: { key: string | number }) {
  const item = menuItems.find(m => m.key === String(key))
  if (item) {
    router.push(item.path)
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>

<template>
  <Layout class="default-layout">
    <Sider
      v-model:collapsed="collapsed"
      :width="260"
      :collapsed-width="80"
      theme="light"
      class="layout-sider"
    >
      <div class="sider-logo" :class="{ collapsed }">
        <span class="logo-text">{{ collapsed ? '谣' : '谣言透镜' }}</span>
      </div>

      <Menu
        mode="inline"
        :selected-keys="selectedKeys"
        class="sider-menu"
        @click="handleMenuClick"
      >
        <Menu.Item v-for="item in menuItems" :key="item.key">
          <component :is="item.icon" />
          <span>{{ item.label }}</span>
        </Menu.Item>
      </Menu>
    </Sider>

    <Layout>
      <Header class="layout-header">
        <div class="header-left">
          <Button
            type="text"
            @click="collapsed = !collapsed"
            class="collapse-btn"
          >
            <template #icon>
              <span class="collapse-icon">{{ collapsed ? '>' : '<' }}</span>
            </template>
          </Button>
        </div>

        <div class="header-right">
          <Dropdown placement="bottomRight">
            <div class="user-info">
              <Avatar :size="32" class="user-avatar">
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </Avatar>
              <span class="user-name">{{ authStore.user?.username }}</span>
            </div>
            <template #overlay>
              <Menu>
                <Menu.Item key="settings" @click="router.push('/settings')">
                  <SettingOutlined />
                  <span>账户设置</span>
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item key="logout" @click="handleLogout">
                  <LogoutOutlined />
                  <span>退出登录</span>
                </Menu.Item>
              </Menu>
            </template>
          </Dropdown>
        </div>
      </Header>

      <Content class="layout-content">
        <RouterView />
      </Content>
    </Layout>
  </Layout>
</template>

<style scoped>
.default-layout {
  min-height: 100vh;
}

.layout-sider {
  border-right: 1px solid var(--color-border);
  background: var(--color-bg) !important;
}

.sider-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.sider-logo.collapsed {
  justify-content: center;
  padding: 0;
}

.logo-text {
  font-family: var(--font-serif);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  letter-spacing: -0.02em;
}

.sider-menu {
  padding: var(--space-4);
  background: transparent !important;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--space-6);
  background: var(--color-bg) !important;
  border-bottom: 1px solid var(--color-border);
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: var(--text-lg);
}

.collapse-icon {
  font-family: var(--font-mono);
  font-weight: var(--font-bold);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.user-info:hover {
  background-color: var(--color-bg-secondary);
}

.user-avatar {
  background-color: var(--color-text);
  color: var(--color-bg);
  font-weight: var(--font-semibold);
}

.user-name {
  font-weight: var(--font-medium);
}

.layout-content {
  padding: var(--space-8);
  background: var(--color-bg-secondary);
  min-height: calc(100vh - 64px);
}
</style>
