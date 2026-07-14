import axios from 'axios'

// One axios instance used by the whole app.
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
})

// Attach the JWT token (if we have one) to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// If the token is invalid/expired (401), send the user back to login.
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
