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
    message.error('Please fill in all fields')
    return
  }

  if (formState.password !== formState.confirmPassword) {
    message.error('Passwords do not match')
    return
  }

  if (formState.password.length < 6) {
    message.error('Password must be at least 6 characters')
    return
  }

  loading.value = true
  try {
    await authStore.register(formState.email, formState.username, formState.password)
    message.success('Registration successful')
    router.push('/')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-view">
    <h2 class="form-title">Create Account</h2>
    <p class="form-subtitle">Join RumorLens to start detecting rumors</p>

    <Form
      :model="formState"
      layout="vertical"
      class="register-form"
      @finish="handleSubmit"
    >
      <Form.Item label="Email" name="email">
        <Input
          v-model:value="formState.email"
          size="large"
          placeholder="your@email.com"
        />
      </Form.Item>

      <Form.Item label="Username" name="username">
        <Input
          v-model:value="formState.username"
          size="large"
          placeholder="Choose a username"
        />
      </Form.Item>

      <Form.Item label="Password" name="password">
        <Input.Password
          v-model:value="formState.password"
          size="large"
          placeholder="At least 6 characters"
        />
      </Form.Item>

      <Form.Item label="Confirm Password" name="confirmPassword">
        <Input.Password
          v-model:value="formState.confirmPassword"
          size="large"
          placeholder="Confirm your password"
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
          Create Account
        </Button>
      </Form.Item>
    </Form>

    <p class="form-footer">
      Already have an account?
      <router-link to="/auth/login" class="link-underline">
        Sign in
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
