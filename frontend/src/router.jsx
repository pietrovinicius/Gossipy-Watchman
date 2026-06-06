import { createBrowserRouter } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'

// Lazy-loaded pages para não bloquear o bundle inicial
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Upload = lazy(() => import('./pages/Upload'))
const People = lazy(() => import('./pages/People'))
const PersonDetail = lazy(() => import('./pages/PersonDetail'))

const Loading = () => (
  <div className="flex items-center justify-center min-h-screen bg-bg">
    <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
  </div>
)

function Protected({ children }) {
  return (
    <ProtectedRoute>
      <Suspense fallback={<Loading />}>{children}</Suspense>
    </ProtectedRoute>
  )
}

const router = createBrowserRouter([
  { path: '/', element: <Login /> },
  { path: '/dashboard', element: <Protected><Dashboard /></Protected> },
  { path: '/upload', element: <Protected><Upload /></Protected> },
  { path: '/people', element: <Protected><People /></Protected> },
  { path: '/people/:id', element: <Protected><PersonDetail /></Protected> },
])

export default router
