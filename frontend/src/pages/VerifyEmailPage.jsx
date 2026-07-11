import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import apiClient from '../api/client.js'

function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [status, setStatus] = useState('loading') // 'loading' | 'success' | 'error'
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setStatus('error')
        setErrorMessage('Посилання пошкоджене або неповне.')
        return
      }

      try {
        await apiClient.post('/auth/verify-email', { token })
        setStatus('success')
      } catch (err) {
        setStatus('error')
        setErrorMessage(
          err.response?.data?.detail ||
            'Не вдалося підтвердити email. Спробуйте ще раз.'
        )
      }
    }

    verify()
    // Токен не змінюється протягом життя компонента - викликаємо лише один раз.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="auth-page">
      <div className="auth-card">
        {status === 'loading' && (
          <>
            <h1 className="auth-title">Підтверджуємо email...</h1>
            <p className="auth-subtitle">Зачекайте, будь ласка</p>
          </>
        )}

        {status === 'success' && (
          <>
            <h1 className="auth-title">Email підтверджено!</h1>
            <p className="text-success">
              Дякуємо, ваш email успішно підтверджено.
            </p>
            <p className="auth-subtitle">
              <Link to="/login">Перейти до входу</Link>
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <h1 className="auth-title">Не вдалося підтвердити</h1>
            <p className="text-error">{errorMessage}</p>
            <p className="auth-subtitle">
              Посилання могло застаріти (діє 24 години).
            </p>
          </>
        )}
      </div>
    </div>
  )
}

export default VerifyEmailPage