import http from './http.js'

export const createPrediction = (features, sequence) => http.post('/api/predictions', { features, sequence }).then(response => response.data)
export const getLatestForecast = () => http.get('/api/forecasts/latest').then(response => response.data)
export const getForecastHistory = (limit = 50) => http.get(`/api/forecasts/history?limit=${limit}`).then(response => response.data)
