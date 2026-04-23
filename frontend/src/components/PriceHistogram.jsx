import { useEffect, useRef } from 'react'
import {
  Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend,
} from 'chart.js'
import { CLUSTER_COLORS } from '../utils/constants'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

// Warm cluster palette for light background
const WARM_CLUSTER_COLORS = [
  '#C96442', '#1D6FA4', '#2E7D52', '#B45309',
  '#7C3AED', '#0891B2', '#DC2626', '#059669',
]

function buildBins(prices, binCount = 20) {
  if (!prices.length) return { labels: [], data: [] }
  const min  = Math.min(...prices)
  const max  = Math.max(...prices)
  const step = (max - min) / binCount || 1
  const bins = Array.from({ length: binCount }, (_, i) => ({
    label: `${(min + i * step).toFixed(0)}`,
    count: 0,
  }))
  prices.forEach((p) => {
    const idx = Math.min(Math.floor((p - min) / step), binCount - 1)
    bins[idx].count++
  })
  return { labels: bins.map((b) => b.label), data: bins.map((b) => b.count) }
}

export default function PriceHistogram({ results = [] }) {
  const canvasRef = useRef(null)
  const chartRef  = useRef(null)

  useEffect(() => {
    if (!canvasRef.current) return

    const prices   = results.map((r) => parseFloat(r.price_mad ?? r.price ?? 0))
    const clusters = results.map((r) => r.analysis?.cluster_kmeans ?? null)
    const hasClusters = clusters.some((c) => c !== null)

    const { labels, data } = buildBins(prices)

    let bgColors = data.map(() => 'rgba(201, 100, 66, 0.65)')
    if (hasClusters) {
      const min  = Math.min(...prices)
      const max  = Math.max(...prices)
      const step = (max - min) / labels.length || 1
      bgColors = labels.map((_, i) => {
        const inBin = results.filter((r) => {
          const p = parseFloat(r.price_mad ?? r.price ?? 0)
          return p >= min + i * step && p < min + (i + 1) * step
        })
        const c = inBin[0]?.analysis?.cluster_kmeans
        return c != null ? WARM_CLUSTER_COLORS[c % WARM_CLUSTER_COLORS.length] + 'AA' : 'rgba(201,100,66,0.6)'
      })
    }

    if (chartRef.current) chartRef.current.destroy()

    chartRef.current = new Chart(canvasRef.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Listings',
          data,
          backgroundColor: bgColors,
          borderRadius: 3,
          borderSkipped: false,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#FFFFFF',
            borderColor: '#DDD9D0',
            borderWidth: 1,
            titleColor: '#1A1714',
            bodyColor: '#66635B',
            padding: 12,
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          },
        },
        scales: {
          x: {
            ticks: { color: '#9B978F', maxRotation: 45, font: { size: 10 } },
            grid: { display: false },
            border: { color: '#DDD9D0' },
          },
          y: {
            ticks: { color: '#9B978F', font: { size: 11 } },
            grid: { color: '#ECEAE5' },
            border: { color: '#DDD9D0' },
          },
        },
      },
    })

    return () => chartRef.current?.destroy()
  }, [results])

  if (!results.length) return (
    <div className="empty-state" style={{ height: '260px' }}>
      <span className="empty-state-icon">📊</span>
      <p className="empty-state-title">No data yet</p>
    </div>
  )

  return <div className="chart-wrapper"><canvas ref={canvasRef} /></div>
}
