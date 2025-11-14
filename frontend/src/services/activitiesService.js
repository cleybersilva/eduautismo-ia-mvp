import api from './api'

export const activitiesService = {
  async getAll(params = {}) {
    const response = await api.get('/api/v1/activities', { params })
    return response.data
  },

  async getById(id) {
    const response = await api.get(`/api/v1/activities/${id}`)
    return response.data
  },

  async generate(activityData) {
    const response = await api.post('/api/v1/activities/generate', activityData)
    return response.data
  },

  async update(id, activityData) {
    const response = await api.put(`/api/v1/activities/${id}`, activityData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/api/v1/activities/${id}`)
    return response.data
  },
}
