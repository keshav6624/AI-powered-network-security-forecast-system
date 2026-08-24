import http from './http.js'

export const getModelStatus = () => http.get('/api/models/status').then(response => response.data)
export const getModelPerformance = () => http.get('/api/models/performance').then(response => response.data)
