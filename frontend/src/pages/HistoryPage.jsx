import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { historyApi } from '../api/history'
import { useToast }   from '../context/ToastContext'
import { PLATFORMS, STATUS_COLORS } from '../utils/constants'

function PlatformBadge({ platform }) {
  const p = PLATFORMS.find((x) => x.id === platform)
  return <span className={`badge badge-${platform}`}>{p ? `${p.icon} ${p.name}` : platform}</span>
}

function ConfirmModal({ message, onConfirm, onCancel }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <h2 className="modal-title">Confirm Delete</h2>
        <p className="modal-body">{message}</p>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
          <button id="confirm-delete-btn" className="btn btn-danger" onClick={onConfirm}>Delete</button>
        </div>
      </div>
    </div>
  )
}

export default function HistoryPage() {
  const navigate      = useNavigate()
  const { showToast } = useToast()

  const [items,        setItems]        = useState([])
  const [page,         setPage]         = useState(1)
  const [total,        setTotal]        = useState(0)
  const [loading,      setLoading]      = useState(true)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const PAGE_SIZE  = 20
  const totalPages = Math.ceil(total / PAGE_SIZE) || 1

  async function load(p = 1) {
    setLoading(true)
    try {
      const res  = await historyApi.getHistory(p)
      const data = res.data
      setItems(data.results ?? data ?? [])
      setTotal(data.count ?? (data.results?.length ?? 0))
    } catch {
      showToast('Failed to load history', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(page) }, [page])

  async function confirmDelete() {
    try {
      await historyApi.deleteHistory(deleteTarget)
      setItems((prev) => prev.filter((i) => i.id !== deleteTarget))
      setTotal((t) => t - 1)
      showToast('Search deleted', 'success')
    } catch {
      showToast('Failed to delete', 'error')
    } finally {
      setDeleteTarget(null)
    }
  }

  function formatDate(str) {
    return new Date(str).toLocaleString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  }

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 className="page-title">Search History</h1>
          <p className="page-subtitle">All your previous market research queries</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/search')}>
          New Search
        </button>
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: '78px', borderRadius: '12px' }} />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="card empty-state" style={{ padding: '64px 24px' }}>
          <span className="empty-state-icon">🕓</span>
          <p className="empty-state-title">No searches yet</p>
          <p className="empty-state-desc">Start by searching for a product to compare prices.</p>
          <button className="btn btn-primary" onClick={() => navigate('/search')} style={{ marginTop: '8px' }}>
            Start searching
          </button>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
            {items.map((item) => (
              <div
                key={item.id}
                className="card"
                style={{
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  flexWrap: 'wrap',
                  cursor: 'pointer',
                  transition: 'transform var(--transition-fast), box-shadow var(--transition-fast)',
                }}
                onClick={() => navigate(`/results/${item.id}`)}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateX(3px)'; e.currentTarget.style.boxShadow = 'var(--shadow-sm)' }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' }}
              >
                {/* Icon */}
                <div style={{
                  width: '38px', height: '38px', borderRadius: '10px',
                  background: 'var(--brand-light)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  fontSize: '18px', flexShrink: 0,
                }}>
                  🔍
                </div>

                {/* Query + platforms */}
                <div style={{ flex: 1, minWidth: '140px' }}>
                  <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--text-primary)', marginBottom: '5px' }}>
                    {item.query}
                  </div>
                  <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                    {(item.platforms ?? []).map((p) => <PlatformBadge key={p} platform={p} />)}
                  </div>
                </div>

                {/* Status */}
                <span className={`badge badge-${STATUS_COLORS[item.status] || 'neutral'}`}>
                  {item.status}
                </span>

                {/* Date */}
                <span style={{ fontSize: '12px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                  {formatDate(item.created_at)}
                </span>

                {/* Delete */}
                <button
                  id={`delete-search-${item.id}`}
                  className="btn btn-danger btn-sm"
                  onClick={(e) => { e.stopPropagation(); setDeleteTarget(item.id) }}
                  title="Delete"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              ← Previous
            </button>
            <span className="pagination-info">Page {page} of {totalPages} · {total} searches</span>
            <button className="btn btn-secondary btn-sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
              Next →
            </button>
          </div>
        </>
      )}

      {deleteTarget && (
        <ConfirmModal
          message="Delete this search and all its data? This action cannot be undone."
          onConfirm={confirmDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  )
}
