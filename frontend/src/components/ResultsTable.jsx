import { ExternalLink } from 'lucide-react'
import { PLATFORMS, CONDITION_LABELS } from '../utils/constants'

function PlatformBadge({ platform }) {
  const p = PLATFORMS.find((x) => x.id === platform)
  return <span className={`badge badge-${platform}`}>{p ? `${p.icon} ${p.name}` : platform}</span>
}

export default function ResultsTable({ results = [], loading = false, total = 0, page = 1, pageSize = 20, onPageChange }) {
  const totalPages = Math.ceil(total / pageSize) || 1

  if (loading) {
    return (
      <div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: '48px', borderRadius: '8px', marginBottom: '8px' }} />
        ))}
      </div>
    )
  }

  if (!results.length) {
    return (
      <div className="empty-state">
        <span className="empty-state-icon">🔍</span>
        <p className="empty-state-title">No results match your filters</p>
        <p className="empty-state-desc">Try adjusting the platform or sort options</p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Platform</th>
              <th>Price (MAD)</th>
              <th>Condition</th>
              <th>Seller ★</th>
              <th>Cluster</th>
              <th>Anomaly</th>
              <th>Deal Score</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => {
              const analysis   = r.analysis ?? {}
              const isAnomaly  = analysis.is_anomaly
              const dealScore  = analysis.deal_score != null ? `${(analysis.deal_score * 100).toFixed(1)}%` : '—'
              const cluster    = analysis.cluster_kmeans != null ? `#${analysis.cluster_kmeans}` : '—'

              return (
                <tr key={r.id ?? i} className={isAnomaly ? 'anomaly-row' : ''}>
                  <td style={{ maxWidth: '260px' }}>
                    <span style={{
                      display: 'block',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                    }} title={r.title}>
                      {r.title}
                    </span>
                  </td>
                  <td><PlatformBadge platform={r.platform} /></td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    {Number(r.price_mad ?? r.price ?? 0).toFixed(2)}
                  </td>
                  <td style={{ fontSize: '12px' }}>
                    {r.condition ? (CONDITION_LABELS[r.condition] ?? r.condition) : '—'}
                  </td>
                  <td style={{ fontSize: '13px' }}>
                    {r.seller_rating != null ? `${Number(r.seller_rating).toFixed(1)} ★` : '—'}
                  </td>
                  <td>
                    {cluster !== '—'
                      ? <span className="badge badge-info">{cluster}</span>
                      : <span style={{ color: 'var(--text-muted)' }}>—</span>
                    }
                  </td>
                  <td>
                    {isAnomaly
                      ? <span className="badge badge-warning">⚠️ Anomaly</span>
                      : <span className="badge badge-neutral">Normal</span>
                    }
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--color-success)' }}>{dealScore}</td>
                  <td>
                    {r.url
                      ? <a href={r.url} target="_blank" rel="noopener noreferrer"
                          className="btn btn-ghost btn-sm" style={{ padding: '4px 8px' }}>
                          <ExternalLink size={13} />
                        </a>
                      : '—'
                    }
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <button
          className="btn btn-secondary btn-sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          ← Prev
        </button>
        <span className="pagination-info">Page {page} of {totalPages} &nbsp;·&nbsp; {total} results</span>
        <button
          className="btn btn-secondary btn-sm"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  )
}
