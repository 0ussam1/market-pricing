import axios from 'axios'

const api = axios.create({
  baseURL: '/api/',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// 401 interceptor — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Avoid redirect loop on the login/register pages
      if (!window.location.pathname.startsWith('/login') &&
          !window.location.pathname.startsWith('/register')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
