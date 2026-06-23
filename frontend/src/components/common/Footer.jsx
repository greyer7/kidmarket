import { Link } from 'react-router-dom'

function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div className="footer__brand">
          <Link to="/" className="footer__logo">
            🧸 KidMarket
          </Link>
          <p className="footer__tagline">
            Маркетплейс дитячих товарів
          </p>
        </div>

        <div className="footer__links">
          <div className="footer__col">
            <h4 className="footer__col-title">Навігація</h4>
            <Link to="/" className="footer__link">Оголошення</Link>
            <Link to="/register" className="footer__link">Реєстрація</Link>
            <Link to="/login" className="footer__link">Увійти</Link>
          </div>
        </div>
      </div>

      <div className="footer__bottom">
        <div className="container">
          <p className="footer__copy">
            © {currentYear} KidMarket. Всі права захищені.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer