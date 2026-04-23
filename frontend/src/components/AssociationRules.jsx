import { useState } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'

export default function AssociationRules({ rules = [] }) {
  const [sortKey, setSortKey]   = useState('lift')
  const [sortDir, setSortDir]   = useState('desc')

  if (!rules.length) {
    return (
      <div className="empty-state" style={{ minHeight: '160px' }}>
        <span className="empty-state-icon">🔗</span>
        <p className="empty-state-title">Not enough data for association rules</p>
        <p className="empty-state-desc">Minimum 30 results required</p>
      </div>
    )
  }

  function handleSort(key) {
    if (key === sortKey) setSortDir((d) => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
  }

  const sorted = [...rules].sort((a, b) => {
    const va = a[sortKey], vb = b[sortKey]
    if (typeof va === 'number') return sortDir === 'asc' ? va - vb : vb - va
    return sortDir === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va))
  })

  function SortIcon({ col }) {
    if (col !== sortKey) return null
    return sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />
  }

  const cols = [
    { key: 'antecedent', label: 'Antecedent' },
    { key: 'consequent', label: 'Consequent' },
    { key: 'support',    label: 'Support %' },
    { key: 'confidence', label: 'Confidence %' },
    { key: 'lift',       label: 'Lift' },
  ]

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c.key} onClick={() => handleSort(c.key)} style={{ whiteSpace: 'nowrap' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  {c.label} <SortIcon col={c.key} />
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((r, i) => {
            const ant = Array.isArray(r.antecedent) ? r.antecedent.join(', ') : r.antecedent
            const con = Array.isArray(r.consequent) ? r.consequent.join(', ') : r.consequent
            return (
              <tr key={i}>
                <td><span className="badge badge-neutral">{ant}</span></td>
                <td><span className="badge badge-info">{con}</span></td>
                <td>{(r.support * 100).toFixed(1)}%</td>
                <td>{(r.confidence * 100).toFixed(1)}%</td>
                <td style={{ fontWeight: 600, color: r.lift > 1.5 ? 'var(--color-success)' : 'var(--text-secondary)' }}>
                  {r.lift.toFixed(3)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
