import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import apiClient from '../api/client.js'

function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Паролі не збігаються')
      return
    }

    setLoading(true)

    try {
      await apiClient.post('/auth/reset-password', {
        token,
        new_password: newPassword,
      })
      setSuccess(true)
      setTimeout(() => navigate('/login', { replace: true }), 2000)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Не вдалося змінити пароль. Спробуйте ще раз.'
      )
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h1 className="auth-title">Недійсне посилання</h1>
          <p className="text-error">
            Посилання для скидання пароля пошкоджене або неповне.
          </p>
          <p className="auth-subtitle">
            <Link to="/forgot-password">Запросити нове посилання</Link>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Новий пароль</h1>

        {success ? (
          <p className="text-success">
            Пароль успішно змінено! Переходимо на сторінку входу...
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label className="form-label">Новий пароль</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Мінімум 8 символів"
                required
                minLength={8}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Підтвердіть пароль</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Введіть пароль ще раз"
                required
                minLength={8}
                className="form-input"
              />
            </div>

            {error && <p className="text-error">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary auth-submit"
            >
              {loading ? 'Збереження...' : 'Зберегти новий пароль'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default ResetPasswordPage