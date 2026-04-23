import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchApi } from '../api/search'
import { useToast } from '../context/ToastContext'
import SearchForm from '../components/SearchForm'

export default function SearchPage() {
  const navigate    = useNavigate()
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)

  async function handleSearch(query, platforms) {
    setLoading(true)
    try {
      const res = await searchApi.createSearch(query, platforms)
      navigate(`/results/${res.data.id}`)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to start search. Please try again.'
      showToast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', paddingTop: '24px' }}>
      <div style={{ maxWidth: '720px', width: '100%', margin: '0 auto' }}>
        <SearchForm onSubmit={handleSearch} loading={loading} />
      </div>
    </div>
  )
}
