import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '../api/client.js'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)

        const response = await apiClient.post('/auth/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })

        const { access_token } = response.data

        const profileResponse = await apiClient.get('/users/me', {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        })

        set({
          token: access_token,
          user: profileResponse.data,
          isAuthenticated: true,
        })
      },

      register: async (email, password, full_name) => {
        await apiClient.post('/auth/register', {
          email,
          password,
          full_name,
        })
      },

      // Використовується після повернення з Google OAuth (GoogleCallbackPage) -
      // токен вже готовий (виданий бекендом), тут лише зберігаємо його
      // і підтягуємо профіль користувача, як і при звичайному логіні.
      loginWithGoogleToken: async (token) => {
        const profileResponse = await apiClient.get('/users/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        set({
          token,
          user: profileResponse.data,
          isAuthenticated: true,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      updateUser: (userData) => {
        set((state) => ({
          user: { ...state.user, ...userData },
        }))
      },
    }),
    {
      name: 'kidmarket-auth',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)