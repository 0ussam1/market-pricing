import { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]           = useState(null)
  const [isLoggedIn, setLoggedIn] = useState(false)
  const [loading, setLoading]     = useState(true)

  // Check auth on mount by calling the protected endpoint
  useEffect(() => {
    authApi.me()
      .then((res) => {
        setUser(res.data)
        setLoggedIn(true)
      })
      .catch(() => {
        setUser(null)
        setLoggedIn(false)
      })
      .finally(() => setLoading(false))
  }, [])

  async function login(username, password) {
    const res = await authApi.login(username, password)
    // After login, fetch user info
    const me = await authApi.me()
    setUser(me.data)
    setLoggedIn(true)
    return res
  }

  async function logout() {
    try { await authApi.logout() } catch { /* ignore */ }
    setUser(null)
    setLoggedIn(false)
  }

  return (
    <AuthContext.Provider value={{ user, isLoggedIn, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
