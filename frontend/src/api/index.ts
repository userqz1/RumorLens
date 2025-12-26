import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'

const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 600000, // 10分钟超时，批量检测需要更长时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const authStore = useAuthStore()

    if (error.response?.status === 401) {
      // Token expired or invalid
      if (authStore.refreshToken) {
        try {
          // Attempt to refresh token
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: authStore.refreshToken,
          })
          authStore.setTokens(
            response.data.access_token,
            response.data.refresh_token
          )

          // Retry original request
          const originalRequest = error.config
          if (originalRequest) {
            originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
            return api(originalRequest)
          }
        } catch (refreshError) {
          // Refresh failed, logout user
          authStore.logout()
          window.location.href = '/auth/login'
        }
      } else {
        // No refresh token, redirect to login
        authStore.logout()
        window.location.href = '/auth/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
