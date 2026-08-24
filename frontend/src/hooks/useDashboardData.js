import { useCallback, useEffect, useRef, useState } from 'react'
import { getDashboard } from '../services/dashboardApi.js'
import { getReplayStatus } from '../services/replayApi.js'
import { getErrorMessage } from '../utils/errors.js'

const POLL_INTERVAL_MS = 2000

export function useDashboardData() {
  const [data, setData] = useState(null)
  const [replay, setReplay] = useState(null)
  const [error, setError] = useState(null)
  const requestId = useRef(0)

  const load = useCallback(async () => {
    const currentRequest = ++requestId.current
    try {
      const [dashboard, replayStatus] = await Promise.all([getDashboard(), getReplayStatus()])
      if (currentRequest !== requestId.current) return null
      setData(dashboard)
      setReplay(replayStatus)
      setError(null)
      return { dashboard, replay: replayStatus }
    } catch (requestError) {
      if (currentRequest !== requestId.current) return null
      setError(getErrorMessage(requestError, 'Dashboard data could not be reached. Confirm that the API is running, then retry.'))
      return null
    }
  }, [])

  useEffect(() => {
    load()
    const interval = window.setInterval(load, POLL_INTERVAL_MS)
    return () => {
      requestId.current += 1
      window.clearInterval(interval)
    }
  }, [load])

  return { data, setData, replay, error, setError, load }
}
