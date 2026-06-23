import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'

function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { register } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Паролі не співпадають')
      return
    }

    if (password.length < 8) {
      setError('Пароль має бути не менше 8 символів')
      return
    }

    setLoading(true)

    try {
      await register(email, password, fullName)
      navigate('/login')
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Помилка реєстрації. Спробуйте ще раз.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Реєстрація</h1>
        <p className="auth-subtitle">
          Вже є акаунт?{' '}
          <Link to="/login">Увійти</Link>
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Імʼя</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Іван Петренко"
              required
              className="form-input"
            />
          </div>

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
              placeholder="Мінімум 8 символів"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Підтвердження паролю</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Повторіть пароль"
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
            {loading ? 'Завантаження...' : 'Зареєструватись'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default RegisterPage