import axios from 'axios'

export const BACKEND_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BACKEND_URL}/api/v1`,
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Erro desconhecido'
    return Promise.reject(new Error(message))
  }
)

export default api
