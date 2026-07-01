import { createBrowserRouter } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import RouteError from './components/RouteError'
import Login from './pages/Login'

// Lazy-loaded pages para não bloquear o bundle inicial
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const VideoDetail = lazy(() => import('./pages/VideoDetail'))
const VideosCatalog = lazy(() => import('./pages/VideosCatalog'))
const Upload = lazy(() => import('./pages/Upload'))
const People = lazy(() => import('./pages/People'))
const PersonDetail = lazy(() => import('./pages/PersonDetail'))
const Alerts = lazy(() => import('./pages/Alerts'))
const AnalyticsDashboard = lazy(() => import('./pages/AnalyticsDashboard'))
const Employees = lazy(() => import('./pages/Employees'))

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
  { path: '/', element: <Login />, errorElement: <RouteError /> },
  { path: '/dashboard', element: <Protected><Dashboard /></Protected>, errorElement: <RouteError /> },
  { path: '/videos', element: <Protected><VideosCatalog /></Protected>, errorElement: <RouteError /> },
  { path: '/videos/:id', element: <Protected><VideoDetail /></Protected>, errorElement: <RouteError /> },
  { path: '/upload', element: <Protected><Upload /></Protected>, errorElement: <RouteError /> },
  { path: '/people', element: <Protected><People /></Protected>, errorElement: <RouteError /> },
  { path: '/people/:id', element: <Protected><PersonDetail /></Protected>, errorElement: <RouteError /> },
  { path: '/alerts', element: <Protected><Alerts /></Protected>, errorElement: <RouteError /> },
  { path: '/analytics', element: <Protected><AnalyticsDashboard /></Protected>, errorElement: <RouteError /> },
  { path: '/employees', element: <Protected><Employees /></Protected>, errorElement: <RouteError /> },
])

export default router
