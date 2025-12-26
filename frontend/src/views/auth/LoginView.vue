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
    message.error('Please fill in all fields')
    return
  }

  loading.value = true
  try {
    await authStore.login(formState.email, formState.password)
    message.success('Login successful')

    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-view">
    <h2 class="form-title">Sign In</h2>
    <p class="form-subtitle">Enter your credentials to access your account</p>

    <Form
      :model="formState"
      layout="vertical"
      class="login-form"
      @finish="handleSubmit"
    >
      <Form.Item label="Email" name="email">
        <Input
          v-model:value="formState.email"
          size="large"
          placeholder="your@email.com"
        />
      </Form.Item>

      <Form.Item label="Password" name="password">
        <Input.Password
          v-model:value="formState.password"
          size="large"
          placeholder="Enter your password"
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
          Sign In
        </Button>
      </Form.Item>
    </Form>

    <p class="form-footer">
      Don't have an account?
      <router-link to="/auth/register" class="link-underline">
        Create one
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
