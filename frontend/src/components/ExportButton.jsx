import { Download } from 'lucide-react'
import { useState } from 'react'
import { exportApi } from '../api/export'
import { useToast } from '../context/ToastContext'

export default function ExportButton({ searchId, disabled = false }) {
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)

  async function handleExport() {
    setLoading(true)
    try {
      await exportApi.exportCSV(searchId)
      showToast('CSV downloaded successfully!', 'success')
    } catch {
      showToast('Failed to download CSV. Please try again.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      id="export-csv-btn"
      className="btn btn-secondary"
      onClick={handleExport}
      disabled={disabled || loading}
      title={disabled ? 'Available when search is completed' : 'Download results as CSV'}
    >
      {loading ? <><span className="spinner" /> Exporting…</> : <><Download size={15} /> Download CSV</>}
    </button>
  )
}
