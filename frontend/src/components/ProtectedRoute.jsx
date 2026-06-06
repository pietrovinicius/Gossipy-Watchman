import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }) {
  const token = sessionStorage.getItem('gw_token')
  if (!token) return <Navigate to="/" replace />
  return children
}
