import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore.js'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import ListingPage from './pages/ListingPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'
import Header from './components/common/Header.jsx'
import Footer from './components/common/Footer.jsx'

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-wrapper">
        <Header />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/listings/:id" element={<ListingPage />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}

export default App