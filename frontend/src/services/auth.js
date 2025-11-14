import api from './api'

/**
 * Serviço de Autenticação
 * Gerencia login, logout e refresh de tokens JWT
 */

const TOKEN_KEY = 'access_token'
const USER_KEY = 'user'

class AuthService {
  /**
   * Realiza login do usuário
   * @param {string} email - E-mail do usuário
   * @param {string} password - Senha do usuário
   * @returns {Promise<{access_token: string, user: object}>}
   */
  async login(email, password) {
    try {
      // Endpoint POST /api/v1/auth/login conforme backend FastAPI
      const response = await api.post('/api/v1/auth/login', {
        username: email, // Backend espera "username" no OAuth2
        password,
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        transformRequest: [(data) => {
          // Converter para formato form-urlencoded
          return Object.keys(data)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
            .join('&')
        }],
      })

      const { access_token, user } = response.data

      // Salvar token e dados do usuário no localStorage
      this.setToken(access_token)
      this.setUser(user)

      return { access_token, user }
    } catch (error) {
      console.error('Erro no login:', error)

      // Tratar erros específicos
      if (error.response?.status === 401) {
        throw new Error('E-mail ou senha incorretos')
      } else if (error.response?.status === 422) {
        throw new Error('Dados inválidos. Verifique e tente novamente')
      } else if (error.response?.status === 500) {
        throw new Error('Erro no servidor. Tente novamente mais tarde')
      } else if (!error.response) {
        throw new Error('Sem conexão com o servidor. Verifique sua internet')
      }

      throw new Error('Erro ao fazer login. Tente novamente')
    }
  }

  /**
   * Realiza logout do usuário
   */
  logout() {
    this.removeToken()
    this.removeUser()
    window.location.href = '/login'
  }

  /**
   * Verifica se o usuário está autenticado
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.getToken()
  }

  /**
   * Obtém o token JWT armazenado
   * @returns {string|null}
   */
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  }

  /**
   * Armazena o token JWT
   * @param {string} token
   */
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
  }

  /**
   * Remove o token JWT
   */
  removeToken() {
    localStorage.removeItem(TOKEN_KEY)
  }

  /**
   * Obtém os dados do usuário armazenados
   * @returns {object|null}
   */
  getUser() {
    const userStr = localStorage.getItem(USER_KEY)
    if (!userStr) return null

    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }

  /**
   * Armazena os dados do usuário
   * @param {object} user
   */
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  /**
   * Remove os dados do usuário
   */
  removeUser() {
    localStorage.removeItem(USER_KEY)
  }

  /**
   * Obtém o usuário atual (alias para getUser)
   * @returns {object|null}
   */
  getCurrentUser() {
    return this.getUser()
  }

  /**
   * Verifica se o token está expirado
   * @returns {boolean}
   */
  isTokenExpired() {
    const token = this.getToken()
    if (!token) return true

    try {
      // Decodificar payload do JWT (parte do meio)
      const payload = JSON.parse(atob(token.split('.')[1]))

      // Verificar se existe exp e se ainda é válido
      if (!payload.exp) return false

      const now = Math.floor(Date.now() / 1000)
      return payload.exp < now
    } catch {
      return true
    }
  }

  /**
   * Registra novo usuário
   * @param {object} userData - Dados do usuário
   * @returns {Promise<{access_token: string, user: object}>}
   */
  async register(userData) {
    try {
      const response = await api.post('/api/v1/auth/register', userData)
      const { access_token, user } = response.data

      this.setToken(access_token)
      this.setUser(user)

      return { access_token, user }
    } catch (error) {
      console.error('Erro no registro:', error)

      if (error.response?.status === 409) {
        throw new Error('E-mail já cadastrado')
      } else if (error.response?.status === 422) {
        throw new Error('Dados inválidos. Verifique e tente novamente')
      }

      throw new Error('Erro ao criar conta. Tente novamente')
    }
  }

  /**
   * Solicita recuperação de senha
   * @param {string} email
   * @returns {Promise<void>}
   */
  async forgotPassword(email) {
    try {
      await api.post('/api/v1/auth/forgot-password', { email })
    } catch (error) {
      console.error('Erro ao solicitar recuperação de senha:', error)
      throw new Error('Erro ao enviar e-mail de recuperação')
    }
  }

  /**
   * Redefine a senha
   * @param {string} token - Token de recuperação
   * @param {string} newPassword - Nova senha
   * @returns {Promise<void>}
   */
  async resetPassword(token, newPassword) {
    try {
      await api.post('/api/v1/auth/reset-password', {
        token,
        new_password: newPassword,
      })
    } catch (error) {
      console.error('Erro ao redefinir senha:', error)

      if (error.response?.status === 400) {
        throw new Error('Token inválido ou expirado')
      }

      throw new Error('Erro ao redefinir senha')
    }
  }
}

export default new AuthService()
