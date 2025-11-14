import { create } from 'zustand'
import authService from '../services/auth'

export const useAuthStore = create((set) => ({
  user: authService.getCurrentUser(),
  isAuthenticated: authService.isAuthenticated(),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const data = await authService.login(email, password)
      set({ user: data.user, isAuthenticated: true, isLoading: false })
      return data
    } catch (error) {
      const errorMessage = error.message || 'Erro ao fazer login'
      set({ error: errorMessage, isLoading: false })
      throw error
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null })
    try {
      const data = await authService.register(userData)
      set({ user: data.user, isAuthenticated: true, isLoading: false })
      return data
    } catch (error) {
      const errorMessage = error.message || 'Erro ao registrar'
      set({ error: errorMessage, isLoading: false })
      throw error
    }
  },

  logout: () => {
    authService.logout()
    set({ user: null, isAuthenticated: false, error: null })
  },

  clearError: () => set({ error: null }),
}))
