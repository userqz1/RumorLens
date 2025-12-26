import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  // Actions
  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const tokens = await authApi.login({ username: email, password })
      setTokens(tokens.access_token, tokens.refresh_token)
      await fetchUser()
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, username: string, password: string) {
    loading.value = true
    try {
      await authApi.register({ email, username, password })
      // Auto login after registration
      await login(email, password)
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (e) {
      // Ignore logout errors
    } finally {
      user.value = null
      clearTokens()
    }
  }

  async function fetchUser() {
    if (!accessToken.value) return

    loading.value = true
    try {
      user.value = await authApi.getCurrentUser()
    } catch (e) {
      clearTokens()
      user.value = null
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: Partial<User>) {
    loading.value = true
    try {
      user.value = await authApi.updateProfile(data)
    } finally {
      loading.value = false
    }
  }

  async function updatePassword(currentPassword: string, newPassword: string) {
    loading.value = true
    try {
      await authApi.updatePassword(currentPassword, newPassword)
    } finally {
      loading.value = false
    }
  }

  // Initialize - fetch user if token exists
  if (accessToken.value) {
    fetchUser()
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    // Getters
    isAuthenticated,
    isSuperuser,
    // Actions
    setTokens,
    clearTokens,
    login,
    register,
    logout,
    fetchUser,
    updateProfile,
    updatePassword,
  }
})
