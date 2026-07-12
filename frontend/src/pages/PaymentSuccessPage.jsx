import { Link, useSearchParams } from 'react-router-dom'

function PaymentSuccessPage() {
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Оплата успішна! 🎉</h1>
        <p className="text-success">
          Дякуємо за покупку. Продавець отримає сповіщення про оплату.
        </p>
        {sessionId && (
          <p className="text-muted" style={{ fontSize: '12px' }}>
            ID сесії: {sessionId}
          </p>
        )}
        <p className="auth-subtitle">
          <Link to="/">Повернутись на головну</Link>
        </p>
      </div>
    </div>
  )
}

export default PaymentSuccessPage