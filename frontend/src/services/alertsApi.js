import http from './http.js'

export const getAlerts = (limit = 50, severity) => {
  const query = new URLSearchParams({ limit })
  if (severity) query.set('severity', severity)
  return http.get(`/api/alerts?${query}`).then(response => response.data)
}

export const acknowledgeAlert = id => http.post(`/api/alerts/${id}/acknowledge`).then(response => response.data)
export const resolveAlert = id => http.post(`/api/alerts/${id}/resolve`).then(response => response.data)
