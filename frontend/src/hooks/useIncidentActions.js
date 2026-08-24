import { useState } from 'react'
import { acknowledgeAlert, resolveAlert } from '../services/alertsApi.js'
import { getErrorMessage } from '../utils/errors.js'

export function useIncidentActions({ setData, reload }) {
  const [action, setAction] = useState(null)
  const [feedback, setFeedback] = useState(null)

  const update = async (id, status) => {
    setAction({ id, status })
    setFeedback(null)
    try {
      const request = status === 'acknowledged' ? acknowledgeAlert : resolveAlert
      const updated = await request(id)
      setData(current => ({
        ...current,
        recent_alerts: status === 'resolved'
          ? current.recent_alerts.filter(alert => alert.id !== id)
          : current.recent_alerts.map(alert => alert.id === id ? { ...alert, ...updated } : alert),
      }))
      setFeedback({ type: 'success', message: `Incident #${id} ${status}.` })
      await reload()
    } catch (error) {
      setFeedback({
        type: 'error',
        message: getErrorMessage(error, 'The incident could not be updated.'),
      })
    } finally {
      setAction(null)
    }
  }

  return {
    action,
    feedback,
    acknowledge: id => update(id, 'acknowledged'),
    resolve: id => update(id, 'resolved'),
  }
}
