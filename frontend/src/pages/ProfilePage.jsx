import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore.js'
import apiClient from '../api/client.js'
import Loader from '../components/common/Loader.jsx'

function ProfilePage() {
  const { user, updateUser } = useAuthStore()

  const [listings, setListings] = useState([])
  const [listingsLoading, setListingsLoading] = useState(true)

  const [fullName, setFullName] = useState(user?.full_name || '')
  const [profileLoading, setProfileLoading] = useState(false)
  const [profileSuccess, setProfileSuccess] = useState(false)
  const [profileError, setProfileError] = useState('')

  const [activeTab, setActiveTab] = useState('listings')

  const [newListing, setNewListing] = useState({
    title: '',
    description: '',
    price: '',
    condition: 'new',
    category: '',
    image_urls: '',
  })
  const [createLoading, setCreateLoading] = useState(false)
  const [createError, setCreateError] = useState('')
  const [createSuccess, setCreateSuccess] = useState(false)

  const categories = [
    'Одяг', 'Взуття', 'Іграшки', 'Книги',
    'Транспорт', 'Меблі', 'Харчування', 'Інше',
  ]

  const conditions = [
    { value: 'new', label: 'Новий' },
    { value: 'like_new', label: 'Як новий' },
    { value: 'good', label: 'Хороший стан' },
    { value: 'fair', label: 'Задовільний' },
  ]

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const response = await apiClient.get('/listings/my')
        setListings(response.data)
      } catch {
        console.error('Помилка завантаження оголошень')
      } finally {
        setListingsLoading(false)
      }
    }

    fetchListings()
  }, [])

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess(false)
    setProfileLoading(true)

    try {
      const response = await apiClient.patch('/users/me', {
        full_name: fullName,
      })
      updateUser(response.data)
      setProfileSuccess(true)
    } catch (err) {
      setProfileError(
        err.response?.data?.detail || 'Помилка оновлення профілю'
      )
    } finally {
      setProfileLoading(false)
    }
  }

  const handleCreateListing = async (e) => {
    e.preventDefault()
    setCreateError('')
    setCreateSuccess(false)
    setCreateLoading(true)

    try {
      const data = {
        title: newListing.title,
        description: newListing.description,
        price: parseFloat(newListing.price),
        condition: newListing.condition,
        category: newListing.category,
        image_urls: newListing.image_urls
          ? JSON.stringify([newListing.image_urls])
          : null,
      }

      const response = await apiClient.post('/listings/', data)
      setListings([response.data, ...listings])
      setCreateSuccess(true)
      setNewListing({
        title: '',
        description: '',
        price: '',
        condition: 'new',
        category: '',
        image_urls: '',
      })
    } catch (err) {
      setCreateError(
        err.response?.data?.detail || 'Помилка створення оголошення'
      )
    } finally {
      setCreateLoading(false)
    }
  }

  const handleDeleteListing = async (listingId) => {
    if (!window.confirm('Видалити оголошення?')) return

    try {
      await apiClient.delete(`/listings/${listingId}`)
      setListings(listings.filter((l) => l.id !== listingId))
    } catch {
      alert('Помилка при видаленні')
    }
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="profile-avatar">
          {user?.full_name?.[0]?.toUpperCase() || '?'}
        </div>
        <div>
          <h1 className="profile-name">{user?.full_name}</h1>
          <p className="text-muted">{user?.email}</p>
        </div>
      </div>

      <div className="profile-tabs">
        <button
          onClick={() => setActiveTab('listings')}
          className={`profile-tab ${activeTab === 'listings' ? 'profile-tab--active' : ''}`}
        >
          Мої оголошення
        </button>
        <button
          onClick={() => setActiveTab('create')}
          className={`profile-tab ${activeTab === 'create' ? 'profile-tab--active' : ''}`}
        >
          Створити оголошення
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`profile-tab ${activeTab === 'settings' ? 'profile-tab--active' : ''}`}
        >
          Налаштування
        </button>
      </div>

      {activeTab === 'listings' && (
        <div className="profile-content">
          <h2>Мої оголошення</h2>
          {listingsLoading ? (
            <Loader />
          ) : listings.length === 0 ? (
            <p className="text-muted">У вас ще немає оголошень</p>
          ) : (
            <div className="listings-grid">
              {listings.map((listing) => (
                <div key={listing.id} className="listing-card">
                  <div className="listing-card__image">
                    <div className="listing-card__no-image">🧸</div>
                  </div>
                  <div className="listing-card__body">
                    <h3 className="listing-card__title">
                      {listing.title}
                    </h3>
                    <p className="listing-card__price">
                      {listing.price} грн
                    </p>
                    <p className="listing-card__category">
                      {listing.status}
                    </p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                    <a  
                        href={`/listings/${listing.id}`}
                        className="btn btn-outline"
                        style={{ flex: 1, textAlign: 'center' }}
                      >
                        Переглянути
                      </a>
                      <button
                        onClick={() => handleDeleteListing(listing.id)}
                        className="btn btn-outline"
                        style={{ flex: 1 }}
                      >
                        Видалити
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'create' && (
        <div className="profile-content">
          <h2>Нове оголошення</h2>
          <form onSubmit={handleCreateListing} className="create-form">
            <div className="form-group">
              <label className="form-label">Назва</label>
              <input
                type="text"
                value={newListing.title}
                onChange={(e) =>
                  setNewListing({ ...newListing, title: e.target.value })
                }
                placeholder="Назва товару"
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Опис</label>
              <textarea
                value={newListing.description}
                onChange={(e) =>
                  setNewListing({ ...newListing, description: e.target.value })
                }
                placeholder="Опишіть товар"
                required
                rows={4}
                className="form-input"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Ціна (грн)</label>
                <input
                  type="number"
                  value={newListing.price}
                  onChange={(e) =>
                    setNewListing({ ...newListing, price: e.target.value })
                  }
                  placeholder="0"
                  required
                  min="1"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Категорія</label>
                <select
                  value={newListing.category}
                  onChange={(e) =>
                    setNewListing({ ...newListing, category: e.target.value })
                  }
                  required
                  className="form-input"
                >
                  <option value="">Оберіть категорію</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Стан товару</label>
              <select
                value={newListing.condition}
                onChange={(e) =>
                  setNewListing({ ...newListing, condition: e.target.value })
                }
                className="form-input"
              >
                {conditions.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                URL фото (необовʼязково)
              </label>
              <input
                type="url"
                value={newListing.image_urls}
                onChange={(e) =>
                  setNewListing({ ...newListing, image_urls: e.target.value })
                }
                placeholder="https://..."
                className="form-input"
              />
            </div>

            {createError && <p className="text-error">{createError}</p>}

            {createSuccess && (
              <p className="text-success">Оголошення створено успішно!</p>
            )}

            <button
              type="submit"
              disabled={createLoading}
              className="btn btn-primary"
            >
              {createLoading ? 'Створення...' : 'Створити оголошення'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="profile-content">
          <h2>Налаштування профілю</h2>
          <form onSubmit={handleProfileUpdate} className="create-form">
            <div className="form-group">
              <label className="form-label">Імʼя</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email"
                value={user?.email}
                disabled
                className="form-input"
                style={{ opacity: 0.6 }}
              />
              <small className="text-muted">Email не можна змінити</small>
            </div>

            {profileError && <p className="text-error">{profileError}</p>}

            {profileSuccess && (
              <p className="text-success">Профіль оновлено успішно!</p>
            )}

            <button
              type="submit"
              disabled={profileLoading}
              className="btn btn-primary"
            >
              {profileLoading ? 'Збереження...' : 'Зберегти'}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default ProfilePage