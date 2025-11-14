import api from './api'

export const assessmentsService = {
  async getAll(params = {}) {
    const response = await api.get('/api/v1/assessments', { params })
    return response.data
  },

  async getById(id) {
    const response = await api.get(`/api/v1/assessments/${id}`)
    return response.data
  },

  async create(assessmentData) {
    const response = await api.post('/api/v1/assessments', assessmentData)
    return response.data
  },

  async update(id, assessmentData) {
    const response = await api.put(`/api/v1/assessments/${id}`, assessmentData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/assessments/${id}`)
    return response.data
  },

  async getByStudent(studentId) {
    const response = await api.get(`/api/v1/assessments/student/${studentId}`)
    return response.data
  },
}
