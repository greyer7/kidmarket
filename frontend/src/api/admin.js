import apiClient from './client.js'

export const getStats = async () => {
  const response = await apiClient.get('/admin/stats')
  return response.data
}

export const getUsers = async (skip = 0, limit = 50) => {
  const response = await apiClient.get('/admin/users', {
    params: { skip, limit },
  })
  return response.data
}

export const setUserActive = async (userId, isActive) => {
  const response = await apiClient.patch(`/admin/users/${userId}/active`, null, {
    params: { is_active: isActive },
  })
  return response.data
}

export const getListings = async (skip = 0, limit = 50) => {
  const response = await apiClient.get('/admin/listings', {
    params: { skip, limit },
  })
  return response.data
}

export const deleteListing = async (listingId) => {
  const response = await apiClient.delete(`/admin/listings/${listingId}`)
  return response.data
}