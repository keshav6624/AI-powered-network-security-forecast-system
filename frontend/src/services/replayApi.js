import http from './http.js'

export const getReplayStatus = () => http.get('/api/replay/status').then(response => response.data)
export const startReplay = () => http.post('/api/replay/start').then(response => response.data)
export const stopReplay = () => http.post('/api/replay/stop').then(response => response.data)
export const stepReplay = () => http.post('/api/replay/step').then(response => response.data)
export const setReplaySpeed = speed => http.post('/api/replay/speed', { speed }).then(response => response.data)
export const resetReplay = () => http.post('/api/replay/reset').then(response => response.data)
