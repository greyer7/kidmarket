import { useState, useEffect, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'
import { getConversations, getConversationMessages, sendMessage } from '../api/chat.js'
import Loader from '../components/common/Loader.jsx'

function ChatPage() {
  const { user } = useAuthStore()
  const [searchParams] = useSearchParams()
  const [conversations, setConversations] = useState([])
  const [activeConversation, setActiveConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [messagesLoading, setMessagesLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)
  const activeConversationRef = useRef(null)
  const pollingRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadMessages = useCallback(async (conversation) => {
    if (!conversation) return
    try {
      const data = await getConversationMessages(
        conversation.other_user.id,
        conversation.listing_id,
      )
      setMessages(data)
    } catch {
      // Ігноруємо помилки під час періодичного опитування (polling) -
      // тимчасовий збій мережі не повинен "зупиняти" чат чи показувати помилку.
    }
  }, [])

  const startPolling = useCallback((conversation) => {
    if (pollingRef.current) clearInterval(pollingRef.current)
    pollingRef.current = setInterval(() => {
      loadMessages(conversation)
    }, 3000)
  }, [loadMessages])

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  const loadConversations = async () => {
    setLoading(true)
    try {
      const data = await getConversations()
      setConversations(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConversations()
  }, [])

  useEffect(() => {
    const otherUserId = searchParams.get('user')
    const listingId = searchParams.get('listing')

    if (otherUserId && listingId && conversations.length > 0) {
      const found = conversations.find(
        (c) =>
          c.other_user.id === parseInt(otherUserId) &&
          c.listing_id === parseInt(listingId),
      )
      if (found) openConversation(found)
    }
    // openConversation навмисно не в масиві залежностей - це звичайна
    // функція (не useCallback), тому додавання її сюди змушувало б
    // ефект спрацьовувати на КОЖНОМУ рендері, а не лише коли реально
    // змінюються conversations/searchParams.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversations, searchParams])

  const openConversation = async (conversation) => {
    if (pollingRef.current) clearInterval(pollingRef.current)
    setActiveConversation(conversation)
    activeConversationRef.current = conversation
    setMessagesLoading(true)
    try {
      const data = await getConversationMessages(
        conversation.other_user.id,
        conversation.listing_id,
      )
      setMessages(data)
    } finally {
      setMessagesLoading(false)
    }
    startPolling(conversation)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !activeConversation) return
    setSending(true)
    try {
      const msg = await sendMessage(
        newMessage,
        activeConversation.other_user.id,
        activeConversation.listing_id,
      )
      setMessages((prev) => [...prev, msg])
      setNewMessage('')
    } finally {
      setSending(false)
    }
  }

  if (loading) return <Loader />

  return (
    <div className="chat-page">
      <div className="chat-sidebar">
        <h2 className="chat-sidebar__title">Повідомлення</h2>
        {conversations.length === 0 ? (
          <p className="chat-empty">Розмов ще немає</p>
        ) : (
          <ul className="chat-list">
            {conversations.map((conv) => (
              <li
                key={`${conv.listing_id}-${conv.other_user.id}`}
                className={`chat-list__item ${activeConversation?.listing_id === conv.listing_id && activeConversation?.other_user.id === conv.other_user.id ? 'active' : ''}`}
                onClick={() => openConversation(conv)}
              >
                <div className="chat-list__name">{conv.other_user.full_name}</div>
                <div className="chat-list__last">{conv.last_message.content}</div>
                {conv.unread_count > 0 && (
                  <span className="chat-list__badge">{conv.unread_count}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="chat-main">
        {!activeConversation ? (
          <div className="chat-placeholder">
            <p>Виберіть розмову зліва</p>
          </div>
        ) : (
          <>
            <div className="chat-header">
              <strong>{activeConversation.other_user.full_name}</strong>
            </div>

            <div className="chat-messages">
              {messagesLoading ? (
                <Loader />
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`chat-message ${msg.sender_id === user?.id ? 'chat-message--own' : 'chat-message--other'}`}
                  >
                    <p className="chat-message__text">{msg.content}</p>
                    <span className="chat-message__time">
                      {new Date(msg.created_at).toLocaleTimeString('uk-UA', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input" onSubmit={handleSend}>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Напишіть повідомлення..."
                className="form-input"
                disabled={sending}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={sending || !newMessage.trim()}
              >
                {sending ? '...' : 'Надіслати'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}

export default ChatPage