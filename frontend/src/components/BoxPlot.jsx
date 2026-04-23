import { useEffect, useRef } from 'react'
import {
  Chart, LinearScale, CategoryScale, Tooltip, Legend,
} from 'chart.js'

let _registered = false

async function getBoxPlotChart() {
  if (_registered) return
  const mod = await import('@sgratzl/chartjs-chart-boxplot')
  Chart.register(mod.BoxPlotController, mod.BoxAndWiskers, LinearScale, CategoryScale, Tooltip, Legend)
  _registered = true
}

export default function BoxPlot({ results = [] }) {
  const canvasRef = useRef(null)
  const chartRef  = useRef(null)

  useEffect(() => {
    if (!canvasRef.current || !results.length) return

    const prices = results.map((r) => parseFloat(r.price_mad ?? r.price ?? 0))

    getBoxPlotChart().then(() => {
      if (chartRef.current) chartRef.current.destroy()

      chartRef.current = new Chart(canvasRef.current, {
        type: 'boxplot',
        data: {
          labels: ['Price Distribution'],
          datasets: [{
            label: 'All Prices (MAD)',
            data: [prices],
            backgroundColor: 'rgba(201, 100, 66, 0.12)',
            borderColor:     'rgba(201, 100, 66, 0.8)',
            borderWidth: 2,
            outlierBackgroundColor: 'rgba(192, 57, 43, 0.75)',
            outlierBorderColor:     '#C0392B',
            outlierRadius: 5,
            medianColor: '#C96442',
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
            },
          },
          scales: {
            x: {
              ticks: { color: '#9B978F' },
              grid: { display: false },
              border: { color: '#DDD9D0' },
            },
            y: {
              ticks: { color: '#9B978F', callback: (v) => `${v} MAD` },
              grid: { color: '#ECEAE5' },
              border: { color: '#DDD9D0' },
            },
          },
        },
      })
    })

    return () => chartRef.current?.destroy()
  }, [results])

  if (!results.length) return (
    <div className="empty-state" style={{ height: '260px' }}>
      <span className="empty-state-icon">📦</span>
      <p className="empty-state-title">No data yet</p>
    </div>
  )

  return <div className="chart-wrapper"><canvas ref={canvasRef} /></div>
}
