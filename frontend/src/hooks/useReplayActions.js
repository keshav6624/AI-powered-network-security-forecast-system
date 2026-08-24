import { useState } from 'react'
import { resetReplay, setReplaySpeed, startReplay, stepReplay, stopReplay } from '../services/replayApi.js'
import { getErrorMessage } from '../utils/errors.js'

export function useReplayActions({ reload, onError }) {
  const [busyAction, setBusyAction] = useState(null)

  const run = async (name, action) => {
    setBusyAction(name)
    try {
      await action()
      await reload()
    } catch (error) {
      onError(getErrorMessage(error, 'The replay command could not be completed.'))
    } finally {
      setBusyAction(null)
    }
  }

  return {
    busyAction,
    start: () => run('start', startReplay),
    stop: () => run('stop', stopReplay),
    reset: () => run('reset', resetReplay),
    step: () => run('step', stepReplay),
    setSpeed: speed => run('speed', () => setReplaySpeed(speed)),
  }
}
