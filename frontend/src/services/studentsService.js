import api from './api'

export const studentsService = {
  async getAll(params = {}) {
    const response = await api.get('/api/v1/students', { params })
    return response.data
  },

  async getById(id) {
    const response = await api.get(`/api/v1/students/${id}`)
    return response.data
  },

  async create(studentData) {
    const response = await api.post('/api/v1/students', studentData)
    return response.data
  },

  async update(id, studentData) {
    const response = await api.put(`/api/v1/students/${id}`, studentData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/students/${id}`)
    return response.data
  },

  async getActivities(studentId) {
    const response = await api.get(`/api/v1/students/${studentId}/activities`)
    return response.data
  },

  async getAssessments(studentId) {
    const response = await api.get(`/api/v1/students/${studentId}/assessments`)
    return response.data
  },
}
