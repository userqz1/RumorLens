import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()

  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const loading = computed(() => authStore.loading)

  async function login(email: string, password: string) {
    await authStore.login(email, password)
    router.push('/')
  }

  async function register(email: string, username: string, password: string) {
    await authStore.register(email, username, password)
    router.push('/')
  }

  async function logout() {
    await authStore.logout()
    router.push('/auth/login')
  }

  return {
    isAuthenticated,
    user,
    loading,
    login,
    register,
    logout,
  }
}
