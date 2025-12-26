<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Card, Form, Input, Button, Divider, Descriptions, message } from 'ant-design-vue'
import { UserOutlined, MailOutlined, LockOutlined, SaveOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()

// Profile form
const profileForm = reactive({
  username: authStore.user?.username || '',
  email: authStore.user?.email || '',
})
const profileLoading = ref(false)

async function handleUpdateProfile() {
  if (!profileForm.username.trim()) {
    message.warning('用户名不能为空')
    return
  }
  if (!profileForm.email.trim()) {
    message.warning('邮箱不能为空')
    return
  }

  profileLoading.value = true
  try {
    await authStore.updateProfile({
      username: profileForm.username,
      email: profileForm.email,
    })
    message.success('个人信息更新成功')
  } catch (error: any) {
    const detail = error.response?.data?.detail || '更新失败'
    message.error(detail)
  } finally {
    profileLoading.value = false
  }
}

// Password form
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const passwordLoading = ref(false)

async function handleUpdatePassword() {
  if (!passwordForm.currentPassword) {
    message.warning('请输入当前密码')
    return
  }
  if (!passwordForm.newPassword) {
    message.warning('请输入新密码')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    message.warning('新密码长度至少为6位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    message.warning('两次输入的新密码不一致')
    return
  }

  passwordLoading.value = true
  try {
    await authStore.updatePassword(passwordForm.currentPassword, passwordForm.newPassword)
    message.success('密码修改成功')
    // Clear form
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error: any) {
    const detail = error.response?.data?.detail || '密码修改失败'
    if (detail.includes('Incorrect')) {
      message.error('当前密码不正确')
    } else {
      message.error(detail)
    }
  } finally {
    passwordLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}
</script>

<template>
  <div class="settings-view">
    <header class="page-header">
      <h1 class="page-title">账户设置</h1>
      <p class="page-subtitle">
        管理您的账户信息和安全设置
      </p>
    </header>

    <div class="settings-grid">
      <!-- Account Info -->
      <Card class="settings-card" title="账户信息">
        <Descriptions :column="1" bordered size="small">
          <Descriptions.Item label="用户ID">
            <code>{{ authStore.user?.id }}</code>
          </Descriptions.Item>
          <Descriptions.Item label="账户状态">
            <span :class="authStore.user?.is_active ? 'status-active' : 'status-inactive'">
              {{ authStore.user?.is_active ? '正常' : '已禁用' }}
            </span>
          </Descriptions.Item>
          <Descriptions.Item label="账户类型">
            {{ authStore.user?.is_superuser ? '管理员' : '普通用户' }}
          </Descriptions.Item>
          <Descriptions.Item label="注册时间">
            {{ authStore.user?.created_at ? formatDate(authStore.user.created_at) : '-' }}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <!-- Profile Settings -->
      <Card class="settings-card" title="个人信息">
        <Form layout="vertical" @submit.prevent="handleUpdateProfile">
          <Form.Item label="用户名">
            <Input
              v-model:value="profileForm.username"
              :prefix="UserOutlined"
              placeholder="请输入用户名"
            >
              <template #prefix><UserOutlined /></template>
            </Input>
          </Form.Item>

          <Form.Item label="邮箱">
            <Input
              v-model:value="profileForm.email"
              type="email"
              placeholder="请输入邮箱"
            >
              <template #prefix><MailOutlined /></template>
            </Input>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              html-type="submit"
              :loading="profileLoading"
            >
              <template #icon><SaveOutlined /></template>
              保存修改
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <!-- Password Settings -->
      <Card class="settings-card" title="修改密码">
        <Form layout="vertical" @submit.prevent="handleUpdatePassword">
          <Form.Item label="当前密码">
            <Input.Password
              v-model:value="passwordForm.currentPassword"
              placeholder="请输入当前密码"
            >
              <template #prefix><LockOutlined /></template>
            </Input.Password>
          </Form.Item>

          <Form.Item label="新密码">
            <Input.Password
              v-model:value="passwordForm.newPassword"
              placeholder="请输入新密码（至少6位）"
            >
              <template #prefix><LockOutlined /></template>
            </Input.Password>
          </Form.Item>

          <Form.Item label="确认新密码">
            <Input.Password
              v-model:value="passwordForm.confirmPassword"
              placeholder="请再次输入新密码"
            >
              <template #prefix><LockOutlined /></template>
            </Input.Password>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              html-type="submit"
              :loading="passwordLoading"
              danger
            >
              <template #icon><LockOutlined /></template>
              修改密码
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <!-- Danger Zone -->
      <Card class="settings-card danger-card" title="危险操作">
        <p class="danger-text">以下操作不可逆，请谨慎操作</p>
        <Divider />
        <div class="danger-actions">
          <div class="danger-item">
            <div>
              <h4>退出登录</h4>
              <p>退出当前账户，需要重新登录</p>
            </div>
            <Button danger @click="authStore.logout">
              退出登录
            </Button>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  max-width: 800px;
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

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.settings-card {
  border: 1px solid var(--color-border);
}

.status-active {
  color: var(--color-success);
  font-weight: var(--font-semibold);
}

.status-inactive {
  color: var(--color-accent);
  font-weight: var(--font-semibold);
}

.danger-card :deep(.ant-card-head) {
  color: var(--color-accent);
}

.danger-text {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.danger-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.danger-item h4 {
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-1);
}

.danger-item p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
}
</style>
