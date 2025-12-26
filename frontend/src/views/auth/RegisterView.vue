<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Form, Input, Button, message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formState = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
})

const loading = ref(false)

async function handleSubmit() {
  if (!formState.email || !formState.username || !formState.password) {
    message.error('请填写所有字段')
    return
  }

  if (formState.password !== formState.confirmPassword) {
    message.error('两次密码输入不一致')
    return
  }

  if (formState.password.length < 6) {
    message.error('密码长度至少为6位')
    return
  }

  loading.value = true
  try {
    await authStore.register(formState.email, formState.username, formState.password)
    message.success('注册成功')
    router.push('/')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-view">
    <h2 class="form-title">注册账号</h2>
    <p class="form-subtitle">加入谣言透镜，开始检测谣言</p>

    <Form
      :model="formState"
      layout="vertical"
      class="register-form"
      @finish="handleSubmit"
    >
      <Form.Item label="邮箱" name="email">
        <Input
          v-model:value="formState.email"
          size="large"
          placeholder="your@email.com"
        />
      </Form.Item>

      <Form.Item label="用户名" name="username">
        <Input
          v-model:value="formState.username"
          size="large"
          placeholder="请输入用户名"
        />
      </Form.Item>

      <Form.Item label="密码" name="password">
        <Input.Password
          v-model:value="formState.password"
          size="large"
          placeholder="至少6位字符"
        />
      </Form.Item>

      <Form.Item label="确认密码" name="confirmPassword">
        <Input.Password
          v-model:value="formState.confirmPassword"
          size="large"
          placeholder="请再次输入密码"
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
          注册
        </Button>
      </Form.Item>
    </Form>

    <p class="form-footer">
      已有账号？
      <router-link to="/auth/login" class="link-underline">
        立即登录
      </router-link>
    </p>
  </div>
</template>

<style scoped>
.register-view {
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

.register-form {
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
