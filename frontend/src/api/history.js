import api from './axios'

export const historyApi = {
  /** Get paginated search history — GET /api/search/?page=N */
  getHistory(page = 1) {
    return api.get('search/', { params: { page } })
  },

  /** Delete a search record — DELETE /api/search/:id/ */
  deleteHistory(id) {
    return api.delete(`search/${id}/`)
  },
}
