import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'
import apiClient from '../api/client.js'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)

  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Помилка входу. Спробуйте ще раз.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError('')
    setGoogleLoading(true)

    try {
      const response = await apiClient.get('/auth/google')
      // Переходимо на сторінку Google - користувач залишить наш сайт,
      // тому це window.location, а не react-router navigate.
      window.location.href = response.data.authorize_url
    } catch (err) {
      setError('Не вдалося розпочати вхід через Google. Спробуйте ще раз.')
      setGoogleLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Вхід</h1>
        <p className="auth-subtitle">
          Немає акаунту?{' '}
          <Link to="/register">Зареєструватись</Link>
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введіть пароль"
              required
              className="form-input"
            />
          </div>

          {error && (
            <p className="text-error">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary auth-submit"
          >
            {loading ? 'Завантаження...' : 'Увійти'}
          </button>
        </form>

        <div className="auth-divider">або</div>

        <button
          type="button"
          onClick={handleGoogleLogin}
          disabled={googleLoading}
          className="btn btn-google auth-submit"
        >
          {googleLoading ? 'Перенаправлення...' : 'Увійти через Google'}
        </button>
      </div>
    </div>
  )
}

export default LoginPage