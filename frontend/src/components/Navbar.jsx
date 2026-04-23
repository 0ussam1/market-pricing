import { NavLink, useNavigate } from 'react-router-dom'
import { Search, History, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate         = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      {/* Brand */}
      <NavLink to="/search" className="navbar-brand">
        <span className="navbar-brand-dot" />
        PriceScope
      </NavLink>

      {/* Nav links */}
      <div className="navbar-links">
        <NavLink
          to="/search"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Search size={14} />
          <span>Search</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <History size={14} />
          <span>History</span>
        </NavLink>
      </div>

      {/* User area */}
      <div className="navbar-user">
        {user?.username && (
          <span className="navbar-username">{user.username}</span>
        )}
        <button className="btn btn-ghost btn-sm" onClick={handleLogout} title="Logout">
          <LogOut size={14} />
          <span>Sign out</span>
        </button>
      </div>
    </nav>
  )
}
