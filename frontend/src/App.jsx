import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore.js'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import ForgotPasswordPage from './pages/ForgotPasswordPage.jsx'
import ResetPasswordPage from './pages/ResetPasswordPage.jsx'
import GoogleCallbackPage from './pages/GoogleCallbackPage.jsx'
import ListingPage from './pages/ListingPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'
import AdminPage from './pages/AdminPage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import Header from './components/common/Header.jsx'
import Footer from './components/common/Footer.jsx'

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function AdminRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!user?.is_admin) return <Navigate to="/" replace />
  return children
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
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/auth/callback" element={<GoogleCallbackPage />} />
            <Route path="/listings/:id" element={<ListingPage />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <ChatPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminPage />
                </AdminRoute>
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