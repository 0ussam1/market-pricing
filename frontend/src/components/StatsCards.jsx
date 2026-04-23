const STATS = [
  { key: 'count',    label: 'Results',       icon: '📊', fmt: (v) => v },
  { key: 'mean',     label: 'Mean Price',     icon: '📈', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'median',   label: 'Median Price',   icon: '⚖️', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'std',      label: 'Std Deviation',  icon: '〰️', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'variance', label: 'Variance',       icon: '📉', fmt: (v) => Number(v).toFixed(2) },
  { key: 'min',      label: 'Min Price',      icon: '⬇️', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'max',      label: 'Max Price',      icon: '⬆️', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'q1',       label: 'Q1 (25th pct)',  icon: '📌', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'q3',       label: 'Q3 (75th pct)',  icon: '📌', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
  { key: 'iqr',      label: 'IQR',            icon: '📏', fmt: (v) => `${Number(v).toFixed(2)} MAD` },
]

function SkeletonCard() {
  return (
    <div className="card stat-card">
      <div className="skeleton" style={{ height: '11px', width: '60%', marginBottom: '10px' }} />
      <div className="skeleton" style={{ height: '26px', width: '80%' }} />
    </div>
  )
}

export default function StatsCards({ stats, loading = false }) {
  if (loading) {
    return (
      <div className="grid-5">
        {STATS.map((s) => <SkeletonCard key={s.key} />)}
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="grid-5 animate-fade-in">
      {STATS.map((s) => (
        <div key={s.key} className="card stat-card">
          <div className="stat-card-label">{s.icon} {s.label}</div>
          <div className="stat-card-value">
            {stats[s.key] != null ? s.fmt(stats[s.key]) : '—'}
          </div>
        </div>
      ))}
    </div>
  )
}
