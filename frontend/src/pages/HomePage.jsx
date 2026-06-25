import { useState, useEffect } from 'react'
import apiClient from '../api/client.js'
import Loader from '../components/common/Loader.jsx'

const getFirstImage = (image_urls) => {
  if (!image_urls) return null
  try {
    const urls = JSON.parse(image_urls)
    if (Array.isArray(urls) && urls.length > 0) return urls[0]
    return null
  } catch {
    return null
  }
}

function HomePage() {
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [category, setCategory] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')

  const categories = [
    'Одяг',
    'Взуття',
    'Іграшки',
    'Книги',
    'Транспорт',
    'Меблі',
    'Харчування',
    'Інше',
  ]

  const fetchListings = async () => {
    setLoading(true)
    setError('')

    try {
      const params = {}
      if (category) params.category = category
      if (minPrice) params.min_price = minPrice
      if (maxPrice) params.max_price = maxPrice

      const response = await apiClient.get('/listings/', { params })
      setListings(response.data)
    } catch {
      setError('Не вдалось завантажити оголошення')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchListings()
  }, [])

  const handleFilter = (e) => {
    e.preventDefault()
    fetchListings()
  }

  const handleReset = () => {
    setCategory('')
    setMinPrice('')
    setMaxPrice('')
    fetchListings()
  }

  return (
    <div className="home-page">
      <div className="home-hero">
        <h1 className="home-hero__title">
          Дитячі товари поруч з вами
        </h1>
        <p className="home-hero__subtitle">
          Купуйте і продавайте дитячі речі безпечно і зручно
        </p>
      </div>

      <form onSubmit={handleFilter} className="filter-bar">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="filter-select"
        >
          <option value="">Всі категорії</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        <input
          type="number"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
          placeholder="Ціна від"
          className="filter-input"
          min="0"
        />

        <input
          type="number"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          placeholder="Ціна до"
          className="filter-input"
          min="0"
        />

        <button type="submit" className="btn btn-primary">
          Фільтрувати
        </button>

        <button
          type="button"
          onClick={handleReset}
          className="btn btn-outline"
        >
          Скинути
        </button>
      </form>

      {loading && <Loader />}

      {error && <p className="text-error">{error}</p>}

      {!loading && !error && listings.length === 0 && (
        <p className="home-empty">Оголошень не знайдено</p>
      )}

      {!loading && !error && listings.length > 0 && (
        <div className="listings-grid">
          {listings.map((listing) => {
            const firstImage = getFirstImage(listing.image_urls)
            return (
              <div key={listing.id} className="listing-card">
                <div className="listing-card__image">
                  {firstImage ? (
                    <img src={firstImage} alt={listing.title} />
                  ) : (
                    <div className="listing-card__no-image">🧸</div>
                  )}
                </div>
                <div className="listing-card__body">
                  <h3 className="listing-card__title">{listing.title}</h3>
                  <p className="listing-card__price">
                    {listing.price} грн
                  </p>
                  <p className="listing-card__category">
                    {listing.category}
                  </p>
                  <a
                    href={`/listings/${listing.id}`}
                    className="btn btn-primary listing-card__btn"
                  >
                    Переглянути
                  </a>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default HomePage
