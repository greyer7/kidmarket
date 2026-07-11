import { useEffect, useState } from 'react'
import { getStats, getUsers, setUserActive, getListings, deleteListing } from '../api/admin.js'
import Loader from '../components/common/Loader.jsx'

function AdminPage() {
  const [tab, setTab] = useState('stats')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadTabData(tab)
  }, [tab])

  const loadTabData = async (currentTab) => {
    setLoading(true)
    setError(null)
    try {
      if (currentTab === 'stats') {
        setStats(await getStats())
      } else if (currentTab === 'users') {
        setUsers(await getUsers())
      } else if (currentTab === 'listings') {
        setListings(await getListings())
      }
    } catch (err) {
      setError('Не вдалося завантажити дані')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      await setUserActive(userId, !currentStatus)
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: !currentStatus } : u)),
      )
    } catch (err) {
      setError('Не вдалося оновити статус юзера')
    }
  }

  const handleDeleteListing = async (listingId) => {
    if (!confirm('Видалити це оголошення?')) return
    try {
      await deleteListing(listingId)
      setListings((prev) => prev.filter((l) => l.id !== listingId))
    } catch (err) {
      setError('Не вдалося видалити оголошення')
    }
  }

  return (
    <div className="admin-page">
      <h1>Адмін-панель</h1>

      <div className="admin-tabs">
        <button className={tab === 'stats' ? 'active' : ''} onClick={() => setTab('stats')}>
          Статистика
        </button>
        <button className={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}>
          Користувачі
        </button>
        <button className={tab === 'listings' ? 'active' : ''} onClick={() => setTab('listings')}>
          Оголошення
        </button>
      </div>

      {error && <p className="admin-error">{error}</p>}
      {loading ? (
        <Loader />
      ) : (
        <>
          {tab === 'stats' && stats && (
            <div className="admin-stats">
              <div className="stat-card">
                <span>Усього юзерів</span>
                <strong>{stats.total_users}</strong>
              </div>
              <div className="stat-card">
                <span>Активних юзерів</span>
                <strong>{stats.active_users}</strong>
              </div>
              <div className="stat-card">
                <span>Усього оголошень</span>
                <strong>{stats.total_listings}</strong>
              </div>
              <div className="stat-card">
                <span>Активних оголошень</span>
                <strong>{stats.active_listings}</strong>
              </div>
              <div className="stat-card">
                <span>Продано</span>
                <strong>{stats.sold_listings}</strong>
              </div>
            </div>
          )}

          {tab === 'users' && (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Ім&apos;я</th>
                  <th>Статус</th>
                  <th>Дія</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.email}</td>
                    <td>{u.full_name}</td>
                    <td>{u.is_active ? 'Активний' : 'Заблокований'}</td>
                    <td>
                      <button onClick={() => handleToggleActive(u.id, u.is_active)}>
                        {u.is_active ? 'Заблокувати' : 'Активувати'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {tab === 'listings' && (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Назва</th>
                  <th>Ціна</th>
                  <th>Статус</th>
                  <th>Дія</th>
                </tr>
              </thead>
              <tbody>
                {listings.map((l) => (
                  <tr key={l.id}>
                    <td>{l.title}</td>
                    <td>{l.price} грн</td>
                    <td>{l.status}</td>
                    <td>
                      <button onClick={() => handleDeleteListing(l.id)}>Видалити</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  )
}

export default AdminPage