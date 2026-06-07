import { useState, useEffect } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Upload,
  Film,
  Users,
  BadgeCheck,
  Bell,
  BarChart2,
  LogOut,
  Shield,
  Menu,
  X,
  Sun,
  Moon,
} from 'lucide-react'
import api from '../services/api'
import { useTheme } from '../contexts/ThemeContext'

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'
  const label = isDark ? 'Modo claro' : 'Modo escuro'

  return (
    <button
      onClick={toggleTheme}
      title={label}
      aria-label={label}
      className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium
                 text-text-muted hover:bg-card hover:text-text-base
                 transition-colors duration-200 cursor-pointer
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
    >
      {isDark ? (
        <Sun className="w-5 h-5 flex-shrink-0 rotate-180 transition-transform duration-300" aria-hidden="true" />
      ) : (
        <Moon className="w-5 h-5 flex-shrink-0 rotate-0 transition-transform duration-300" aria-hidden="true" />
      )}
      <span className="flex-1 text-left">{label}</span>
    </button>
  )
}

function NavItem({ to, label, Icon, badge, onClick }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
         transition-colors duration-200 cursor-pointer
         ${isActive
           ? 'bg-primary/20 text-primary'
           : 'text-text-muted hover:bg-card hover:text-text-base'
         }`
      }
    >
      <Icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
      <span className="flex-1">{label}</span>
      {badge > 0 && (
        <span className="text-xs bg-primary text-white rounded-full px-1.5 py-0.5 leading-none">
          {badge > 99 ? '99+' : badge}
        </span>
      )}
    </NavLink>
  )
}

export default function Layout({ children }) {
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [unseenCount, setUnseenCount] = useState(0)

  useEffect(() => {
    api.get('/alerts/count').then((res) => setUnseenCount(res.data.unseen)).catch(() => {})
  }, [])

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload',    label: 'Upload',     icon: Upload },
    { to: '/videos',    label: 'Vídeos',     icon: Film },
    { to: '/people',   label: 'Pessoas',    icon: Users },
    { to: '/employees', label: 'Funcionários', icon: BadgeCheck },
    { to: '/alerts',    label: 'Alertas',   icon: Bell, badge: unseenCount },
    { to: '/analytics', label: 'Analytics',  icon: BarChart2 },
  ]

  function handleLogout() {
    sessionStorage.removeItem('gw_token')
    navigate('/')
  }

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className="flex items-center gap-2 px-3 py-4 mb-4 border-b border-border">
        <Shield className="w-6 h-6 text-accent flex-shrink-0" aria-hidden="true" />
        <span className="font-mono font-bold text-text-base text-sm leading-tight">
          Gossipy<br />
          <span className="text-accent">Watchman</span>
        </span>
      </div>

      {/* Nav */}
      <nav aria-label="Menu principal" className="flex-1 space-y-1 px-2">
        {navItems.map(({ to, label, icon: Icon, badge }) => (
          <NavItem key={to} to={to} label={label} Icon={Icon} badge={badge} onClick={() => setSidebarOpen(false)} />
        ))}
      </nav>

      {/* Tema + Logout */}
      <div className="px-2 pb-4 border-t border-border pt-4 space-y-1">
        <ThemeToggle />
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium
                     text-text-muted hover:bg-card hover:text-error-color
                     transition-colors duration-200 cursor-pointer"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          <span>Sair</span>
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-bg">
      {/* Desktop sidebar */}
      <aside
        className="hidden md:flex flex-col w-56 bg-surface border-r border-border fixed inset-y-0 left-0 z-20"
        aria-label="Sidebar"
      >
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 w-56 bg-surface border-r border-border z-40 md:hidden
                    transform transition-transform duration-300
                    ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
        aria-label="Sidebar mobile"
      >
        <button
          onClick={() => setSidebarOpen(false)}
          aria-label="Fechar menu"
          className="absolute top-4 right-4 text-text-muted hover:text-text-base cursor-pointer"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
        {sidebarContent}
      </aside>

      {/* Main content */}
      <main className="flex-1 md:ml-56 min-h-screen">
        {/* Mobile header */}
        <header className="md:hidden flex items-center gap-3 px-4 py-3 bg-surface border-b border-border sticky top-0 z-10">
          <button
            onClick={() => setSidebarOpen(true)}
            aria-label="Abrir menu"
            className="text-text-muted hover:text-text-base cursor-pointer"
          >
            <Menu className="w-5 h-5" aria-hidden="true" />
          </button>
          <Shield className="w-5 h-5 text-accent" aria-hidden="true" />
          <span className="font-mono font-bold text-text-base text-sm">
            Gossipy<span className="text-accent">Watchman</span>
          </span>
        </header>

        <div className="p-4 md:p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
