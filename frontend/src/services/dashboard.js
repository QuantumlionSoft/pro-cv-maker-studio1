import { apiRequest } from './api'

export const dashboardApi = {
  summary: () => apiRequest('GET', '/dashboard/'),
  profile: () => apiRequest('GET', '/profile/'),
  updateProfile: (payload) => apiRequest('PATCH', '/profile/', { body: payload }),
  changePassword: (payload) => apiRequest('POST', '/auth/password/change/', { body: payload }),
}
