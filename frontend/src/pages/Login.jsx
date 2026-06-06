import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Shield } from 'lucide-react'
import axios from 'axios'

const AUTH_URL = 'http://localhost:8000/api/v1/auth/login'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)
      const res = await axios.post(AUTH_URL, form)
      sessionStorage.setItem('gw_token', 'authenticated')
      sessionStorage.setItem('token', res.data.access_token)
      navigate('/dashboard')
    } catch {
      setError('Usuário ou senha incorretos.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent mb-4">
            <Shield className="w-8 h-8 text-white" aria-hidden="true" />
          </div>
          <h1 className="text-3xl font-bold text-text-base font-mono tracking-tight">
            Gossipy<span className="text-accent">Watchman</span>
          </h1>
          <p className="text-text-muted mt-2 text-sm">
            Sistema de análise e identificação facial
          </p>
        </div>

        {/* Form */}
        <div className="card rounded-2xl p-8 shadow-2xl border-border">
          <form onSubmit={handleSubmit} noValidate>
            <div className="space-y-5">
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-medium text-text-muted mb-1.5"
                >
                  Usuário
                </label>
                <input
                  id="username"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full bg-surface border border-border rounded-lg px-3 py-2.5 text-text-base
                             placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary
                             focus:border-transparent transition-colors duration-200"
                  placeholder="admin"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-text-muted mb-1.5"
                >
                  Senha
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPass ? 'text' : 'password'}
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full bg-surface border border-border rounded-lg px-3 py-2.5 pr-10
                               text-text-base placeholder-text-muted focus:outline-none focus:ring-2
                               focus:ring-primary focus:border-transparent transition-colors duration-200"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass((v) => !v)}
                    aria-label={showPass ? 'Ocultar senha' : 'Mostrar senha'}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted
                               hover:text-text-base transition-colors duration-200 cursor-pointer"
                  >
                    {showPass
                      ? <EyeOff className="w-4 h-4" aria-hidden="true" />
                      : <Eye className="w-4 h-4" aria-hidden="true" />
                    }
                  </button>
                </div>
              </div>

              {error && (
                <p role="alert" className="text-sm text-error-color bg-red-950/40 border border-red-800/50
                                           rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary py-2.5 text-base"
              >
                {loading ? 'Verificando...' : 'Entrar'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
