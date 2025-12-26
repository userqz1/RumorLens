import api from './index'
import type { User } from '@/types'

export interface LoginRequest {
  username: string // Actually email
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export const authApi = {
  async login(data: LoginRequest): Promise<TokenResponse> {
    // OAuth2 requires form data
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put<User>('/users/me', data)
    return response.data
  },

  async updatePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.put('/users/me/password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
}
