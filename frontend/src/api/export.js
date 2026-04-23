import api from './axios'

export const exportApi = {
  /**
   * Download results as CSV blob.
   * Triggers a programmatic <a> click to save the file.
   */
  async exportCSV(searchId) {
    const response = await api.get(`export/${searchId}/csv/`, {
      responseType: 'blob',
    })

    const url      = URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }))
    const anchor   = document.createElement('a')
    anchor.href    = url
    anchor.download = `results_${searchId}.csv`
    document.body.appendChild(anchor)
    anchor.click()
    document.body.removeChild(anchor)
    URL.revokeObjectURL(url)
  },
}
