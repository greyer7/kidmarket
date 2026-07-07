import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'

function GoogleCallbackPage() {
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { loginWithGoogleToken } = useAuthStore()

  useEffect(() => {
    const processGoogleLogin = async () => {
      // Токен приходить у fragment (#token=...), а не в query (?token=...) -
      // тому читаємо window.location.hash, а не useSearchParams.
      const hash = window.location.hash // напр. "#token=eyJhbGci..."
      const params = new URLSearchParams(hash.replace('#', ''))
      const token = params.get('token')

      if (!token) {
        setError('Не вдалося отримати токен від Google. Спробуйте ще раз.')
        return
      }

      try {
        await loginWithGoogleToken(token)
        // Одразу прибираємо токен з адресного рядка (щоб не залишався
        // видимим в історії браузера довше, ніж потрібно) і переходимо на головну.
        navigate('/', { replace: true })
      } catch (err) {
        setError('Не вдалося завершити вхід через Google. Спробуйте ще раз.')
      }
    }

    processGoogleLogin()
  }, [loginWithGoogleToken, navigate])

  return (
    <div className="auth-page">
      <div className="auth-card">
        {error ? (
          <>
            <h1 className="auth-title">Помилка входу</h1>
            <p className="text-error">{error}</p>
          </>
        ) : (
          <>
            <h1 className="auth-title">Входимо через Google...</h1>
            <p className="auth-subtitle">Зачекайте, будь ласка</p>
          </>
        )}
      </div>
    </div>
  )
}

export default GoogleCallbackPage