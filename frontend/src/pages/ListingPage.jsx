import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import apiClient from '../api/client.js'
import { useAuthStore } from '../store/authStore.js'
import Loader from '../components/common/Loader.jsx'

function ListingPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated, user } = useAuthStore()

  const [listing, setListing] = useState(null)
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [reviewLoading, setReviewLoading] = useState(false)
  const [reviewError, setReviewError] = useState('')

  const [messageText, setMessageText] = useState('')
  const [messageLoading, setMessageLoading] = useState(false)
  const [messageSent, setMessageSent] = useState(false)

  const [buyLoading, setBuyLoading] = useState(false)
  const [buyError, setBuyError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [listingRes, reviewsRes] = await Promise.all([
          apiClient.get(`/listings/${id}`),
          apiClient.get(`/reviews/listings/${id}`),
        ])
        setListing(listingRes.data)
        setReviews(reviewsRes.data)
      } catch {
        setError('Оголошення не знайдено')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id])

  const handleReview = async (e) => {
    e.preventDefault()
    setReviewError('')
    setReviewLoading(true)

    try {
      const response = await apiClient.post('/reviews/', {
        rating,
        comment,
        listing_id: parseInt(id),
      })
      setReviews([response.data, ...reviews])
      setComment('')
      setRating(5)
    } catch (err) {
      setReviewError(
        err.response?.data?.detail || 'Помилка при відправці відгуку'
      )
    } finally {
      setReviewLoading(false)
    }
  }

  const handleMessage = async (e) => {
    e.preventDefault()
    setMessageLoading(true)

    try {
      await apiClient.post('/chat/messages', {
        content: messageText,
        receiver_id: listing.seller_id,
        listing_id: parseInt(id),
      })
      setMessageSent(true)
      setMessageText('')
    } catch {
      alert('Помилка при відправці повідомлення')
    } finally {
      setMessageLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Видалити оголошення?')) return

    try {
      await apiClient.delete(`/listings/${id}`)
      navigate('/')
    } catch {
      alert('Помилка при видаленні')
    }
  }

  const handleBuy = async () => {
    setBuyError('')
    setBuyLoading(true)

    try {
      const response = await apiClient.post('/payments/create-checkout-session', {
        listing_id: parseInt(id),
      })
      window.location.href = response.data.checkout_url
    } catch (err) {
      setBuyError(
        err.response?.data?.detail || 'Не вдалося розпочати оплату. Спробуйте ще раз.'
      )
      setBuyLoading(false)
    }
  }

  if (loading) return <Loader />
  if (error) return <p className="text-error">{error}</p>
  if (!listing) return null

  const isOwner = user?.id === listing.seller_id
  const images = listing.image_urls
    ? JSON.parse(listing.image_urls)
    : []

  return (
    <div className="listing-page">
      <div className="listing-page__main">
        <div className="listing-page__images">
          {images.length > 0 ? (
            images.map((url, index) => (
              <img key={index} src={url} alt={listing.title} />
            ))
          ) : (
            <div className="listing-page__no-image">🧸</div>
          )}
        </div>

        <div className="listing-page__info">
          <div className="listing-page__header">
            <h1 className="listing-page__title">{listing.title}</h1>
            <p className="listing-page__price">{listing.price} грн</p>
          </div>

          <div className="listing-page__meta">
            <span className="listing-page__badge">
              {listing.category}
            </span>
            <span className="listing-page__badge">
              {listing.condition}
            </span>
            <span className="listing-page__badge listing-page__badge--status">
              {listing.status}
            </span>
          </div>

          <p className="listing-page__description">
            {listing.description}
          </p>

          <div className="listing-page__seller">
            <p className="listing-page__seller-name">
              Продавець: <strong>{listing.seller.full_name}</strong>
            </p>
          </div>

          {isAuthenticated && !isOwner && listing.status === 'active' && (
            <div className="listing-page__buy">
              <button
                onClick={handleBuy}
                disabled={buyLoading}
                className="btn btn-primary"
              >
                {buyLoading ? 'Перенаправлення...' : 'Купити'}
              </button>
              {buyError && <p className="text-error">{buyError}</p>}
            </div>
          )}

          {listing.status === 'sold' && (
            <p className="text-muted">Цей товар вже продано</p>
          )}

          {isOwner && (
            <div className="listing-page__owner-actions">
              <button
                onClick={handleDelete}
                className="btn btn-outline"
              >
                Видалити оголошення
              </button>
            </div>
          )}

          {isAuthenticated && !isOwner && (
            <div className="listing-page__message">
              <h3>Написати продавцю</h3>
              {messageSent ? (
                <div>
                  <p className="text-success">Повідомлення відправлено!</p>
                  <Link
                    to={`/chat?user=${listing.seller_id}&listing=${id}`}
                    className="btn btn-outline"
                    style={{ marginTop: '8px', display: 'inline-block' }}
                  >
                    Перейти до чату
                  </Link>
                </div>
              ) : (
                <form onSubmit={handleMessage}>
                  <textarea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    placeholder="Ваше повідомлення..."
                    required
                    rows={3}
                    className="form-input"
                  />
                  <button
                    type="submit"
                    disabled={messageLoading}
                    className="btn btn-primary"
                    style={{ marginTop: '8px' }}
                  >
                    {messageLoading ? 'Відправка...' : 'Відправити'}
                  </button>
                </form>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="listing-page__reviews">
        <h2>Відгуки</h2>

        {isAuthenticated && !isOwner && (
          <form onSubmit={handleReview} className="review-form">
            <div className="form-group">
              <label className="form-label">Оцінка</label>
              <select
                value={rating}
                onChange={(e) => setRating(parseInt(e.target.value))}
                className="filter-select"
              >
                {[5, 4, 3, 2, 1].map((r) => (
                  <option key={r} value={r}>
                    {'⭐'.repeat(r)} ({r})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Коментар</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Ваш відгук..."
                rows={3}
                className="form-input"
              />
            </div>

            {reviewError && (
              <p className="text-error">{reviewError}</p>
            )}

            <button
              type="submit"
              disabled={reviewLoading}
              className="btn btn-primary"
            >
              {reviewLoading ? 'Відправка...' : 'Залишити відгук'}
            </button>
          </form>
        )}

        <div className="reviews-list">
          {reviews.length === 0 ? (
            <p className="text-muted">Відгуків ще немає</p>
          ) : (
            reviews.map((review) => (
              <div key={review.id} className="review-card">
                <div className="review-card__header">
                  <strong>{review.reviewer.full_name}</strong>
                  <span>{'⭐'.repeat(review.rating)}</span>
                </div>
                {review.comment && (
                  <p className="review-card__comment">
                    {review.comment}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default ListingPage