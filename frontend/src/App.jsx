import { useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import meshImage from './assets/mesh.svg'
import './App.css'

const TOKEN_KEY = 'access_token'

function isAuthenticated() {
  return Boolean(sessionStorage.getItem(TOKEN_KEY))
}

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  return children
}

function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated()) {
    return <Navigate to="/welcome" replace />
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('/api/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data?.detail ?? 'No se pudo iniciar sesión')
        return
      }

      sessionStorage.setItem(TOKEN_KEY, data.access_token)
      navigate('/welcome', { replace: true })
    } catch {
      setError('No se pudo conectar con el backend')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page" style={{ '--mesh-image': `url(${meshImage})` }}>
      <section className="card" aria-label="Inicio de sesión">
        <h1 className="title">Iniciar sesión</h1>
        <p className="subtitle">Accede con las credenciales del backend.</p>

        <form className="form" onSubmit={handleSubmit}>
          <label className="label" htmlFor="username">
            Usuario
          </label>
          <input
            id="username"
            className="input"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />

          <label className="label" htmlFor="password">
            Contraseña
          </label>
          <input
            id="password"
            className="input"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error && <p className="error">{error}</p>}

          <button className="button-primary-pill" type="submit" disabled={loading}>
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>
      </section>
    </main>
  )
}

function WelcomePage() {
  const navigate = useNavigate()

  function handleLogout() {
    sessionStorage.removeItem(TOKEN_KEY)
    navigate('/login', { replace: true })
  }

  return (
    <main className="page" style={{ '--mesh-image': `url(${meshImage})` }}>
      <section className="card" aria-label="Bienvenida">
        <h1 className="title">Bienvenido</h1>
        <p className="subtitle">Tu sesión está activa.</p>
        <button className="button-primary-pill" type="button" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </section>
    </main>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to={isAuthenticated() ? '/welcome' : '/login'} replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/welcome"
          element={
            <ProtectedRoute>
              <WelcomePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
