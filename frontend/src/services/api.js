// Backward-compatible public API facade. New code should import domain modules directly.
export { default } from './http.js'
export { getHealth as health, getDashboard as dashboard, getNetworkGraph as networkGraph } from './dashboardApi.js'
export { getAlerts as alerts, acknowledgeAlert, resolveAlert } from './alertsApi.js'
export {
  getReplayStatus as replayStatus,
  startReplay as replayStart,
  stopReplay as replayStop,
  stepReplay as replayStep,
  setReplaySpeed as replaySpeed,
  resetReplay as replayReset,
} from './replayApi.js'
export {
  createPrediction as predict,
  getLatestForecast as latestForecast,
  getForecastHistory as forecastHistory,
} from './forecastApi.js'
export { getModelStatus as modelStatus, getModelPerformance as modelPerformance } from './modelsApi.js'
