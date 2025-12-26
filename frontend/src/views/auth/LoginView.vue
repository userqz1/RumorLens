<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Input, Button, message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formState = reactive({
  email: '',
  password: '',
})

const loading = ref(false)

async function handleSubmit() {
  if (!formState.email || !formState.password) {
    message.error('请填写所有字段')
    return
  }

  loading.value = true
  try {
    await authStore.login(formState.email, formState.password)
    message.success('登录成功')

    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-view">
    <h2 class="form-title">登录</h2>
    <p class="form-subtitle">请输入您的账号信息</p>

    <Form
      :model="formState"
      layout="vertical"
      class="login-form"
      @finish="handleSubmit"
    >
      <Form.Item label="邮箱" name="email">
        <Input
          v-model:value="formState.email"
          size="large"
          placeholder="your@email.com"
        />
      </Form.Item>

      <Form.Item label="密码" name="password">
        <Input.Password
          v-model:value="formState.password"
          size="large"
          placeholder="请输入密码"
        />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          html-type="submit"
          size="large"
          block
          :loading="loading"
        >
          登录
        </Button>
      </Form.Item>
    </Form>

    <p class="form-footer">
      还没有账号？
      <router-link to="/auth/register" class="link-underline">
        立即注册
      </router-link>
    </p>
  </div>
</template>

<style scoped>
.login-view {
  width: 100%;
}

.form-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}

.form-subtitle {
  color: var(--color-text-muted);
  margin-bottom: var(--space-8);
}

.login-form {
  margin-bottom: var(--space-6);
}

.form-footer {
  text-align: center;
  color: var(--color-text-muted);
}

.form-footer a {
  color: var(--color-text);
  font-weight: var(--font-medium);
  margin-left: var(--space-1);
}
</style>
