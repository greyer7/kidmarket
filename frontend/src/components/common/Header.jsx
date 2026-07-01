import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore.js'

function Header() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="header">
      <div className="container header__inner">
        <Link to="/" className="header__logo">
          🧸 KidMarket
        </Link>

        <nav className="header__nav">
          <Link to="/" className="header__nav-link">
            Оголошення
          </Link>
          {isAuthenticated && (
            <Link to="/chat" className="header__nav-link">
              Повідомлення
            </Link>
          )}
        </nav>

        <div className="header__actions">
          {isAuthenticated ? (
            <>
              {user?.is_admin && (
                <Link to="/admin" className="header__nav-link">
                  Адмін-панель
                </Link>
              )}
              <Link to="/profile" className="header__user">
                {user?.full_name}
              </Link>
              <button onClick={handleLogout} className="btn btn-outline">
                Вийти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">
                Увійти
              </Link>
              <Link to="/register" className="btn btn-primary">
                Реєстрація
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header