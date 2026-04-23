import api from './axios'

export const authApi = {
  login(username, password) {
    return api.post('auth/login/', { username, password })
  },

  register(data) {
    return api.post('auth/register/', data)
  },

  logout() {
    return api.post('auth/logout/')
  },

  /** Check auth status — returns { username } or throws 401 */
  me() {
    return api.get('auth/protected/')
  },
}
