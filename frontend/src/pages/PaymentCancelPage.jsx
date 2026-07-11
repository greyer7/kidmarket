import { Link } from 'react-router-dom'

function PaymentCancelPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Оплату скасовано</h1>
        <p className="auth-subtitle">
          Ви скасували оплату. Товар усе ще доступний для купівлі.
        </p>
        <p className="auth-subtitle">
          <Link to="/">Повернутись на головну</Link>
        </p>
      </div>
    </div>
  )
}

export default PaymentCancelPage