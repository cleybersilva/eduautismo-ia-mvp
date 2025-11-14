import api from './api'

export const authService = {
  async login(email, password) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    const { access_token, token_type, user } = response.data

    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(user))

    return { access_token, token_type, user }
  },

  async register(userData) {
    const response = await api.post('/api/v1/auth/register', userData)
    return response.data
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  getToken() {
    return localStorage.getItem('access_token')
  },

  isAuthenticated() {
    return !!this.getToken()
  },
}
