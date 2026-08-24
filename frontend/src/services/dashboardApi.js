import http from './http.js'

export const getHealth = () => http.get('/api/health').then(response => response.data)
export const getDashboard = () => http.get('/api/dashboard').then(response => response.data)
export const getNetworkGraph = () => http.get('/api/network/graph').then(response => response.data)
