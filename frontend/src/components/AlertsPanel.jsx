function conciseMessage(message='') {
  const [headline,...rest] = message.split(':')
  return { headline: rest.length ? headline : 'Detection event', detail: rest.length ? rest.join(':').trim() : message }
}

export default function AlertsPanel({ alerts, onAck, onResolve, action, feedback }) {
  const openAlerts = (alerts || []).filter(alert => alert.status !== 'resolved')
  const isBusy = id => action?.id === id

  return <article className="panel" id="alerts-panel" tabIndex="-1"><div className="panel-head"><div><h2 className="panel-title">Incident queue</h2><span className="panel-meta" style={{display:'block',marginTop:7}}>Prioritized response actions</span></div><span className={`status-pill ${openAlerts.length?'danger':'safe'}`}>{openAlerts.length} open</span></div>{feedback && <div className={`incident-feedback ${feedback.type === 'error' ? 'error' : ''}`} role={feedback.type === 'error' ? 'alert' : 'status'} aria-live="polite">{feedback.message}</div>}<div className="alert-list">{!openAlerts.length ? <div className="empty-state">No active incidents. Monitoring continues.</div> : openAlerts.map(alert => { const copy=conciseMessage(alert.message);const busy=isBusy(alert.id);return <div className="alert-row" key={alert.id}><div><div className={`alert-severity ${alert.severity.toLowerCase()}`}>{alert.severity}</div><div className="panel-meta" style={{marginTop:7}}>Risk {alert.risk_score}</div></div><div className="alert-message"><strong>{copy.headline}</strong><p>{copy.detail}</p><p className="mono">{new Date(alert.timestamp).toLocaleString()} / {alert.status}</p></div><div className="alert-actions">{alert.status==='active' && <button className="action ghost" disabled={busy} onClick={() => onAck?.(alert.id)}>{busy && action.status==='acknowledged' ? 'Acknowledging…' : 'Acknowledge'}</button>}<button className="action" disabled={busy} onClick={() => onResolve?.(alert.id)}>{busy && action.status==='resolved' ? 'Resolving…' : 'Resolve'}</button></div></div>})}</div></article>
}
