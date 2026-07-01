import apiClient from './client.js'

export const getConversations = async () => {
  const response = await apiClient.get('/chat/conversations')
  return response.data
}

export const getConversationMessages = async (otherUserId, listingId) => {
  const response = await apiClient.get(`/chat/conversations/${otherUserId}/${listingId}`)
  return response.data
}

export const sendMessage = async (content, receiverId, listingId) => {
  const response = await apiClient.post('/chat/messages', {
    content,
    receiver_id: receiverId,
    listing_id: listingId,
  })
  return response.data
}