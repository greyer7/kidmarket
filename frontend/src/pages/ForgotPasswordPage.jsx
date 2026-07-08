import { useState } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client.js'

function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const response = await apiClient.post('/auth/forgot-password', { email })
      setMessage(response.data.message)
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Щось пішло не так. Спробуйте ще раз.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Забули пароль?</h1>
        <p className="auth-subtitle">
          Введіть email, і ми надішлемо посилання для скидання пароля
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

          {message && <p className="text-success">{message}</p>}
          {error && <p className="text-error">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary auth-submit"
          >
            {loading ? 'Надсилання...' : 'Надіслати посилання'}
          </button>
        </form>

        <p className="auth-subtitle">
          <Link to="/login">Повернутись до входу</Link>
        </p>
      </div>
    </div>
  )
}

export default ForgotPasswordPage