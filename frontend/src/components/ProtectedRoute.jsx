import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isLoggedIn, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: '14px',
        background: 'var(--bg-base)',
      }}>
        <div className="spinner spinner-lg" />
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Checking session…</p>
      </div>
    )
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />
  }

  return children
}
