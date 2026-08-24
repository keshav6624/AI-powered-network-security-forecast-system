const classFor = level => (level || 'LOW').toLowerCase()

export default function RiskTimeline({ history }) {
  const points = (history || []).slice(-6)
  return <article className="panel"><div className="panel-head"><h2 className="panel-title">Escalation trail</h2><span className="panel-meta">Oldest → latest</span></div>{points.length ? <div className="risk-sequence">{points.map((point,index) => <div className={`risk-tick ${classFor(point.risk_level)}`} key={`${point.timestamp}-${index}`} title={`${point.risk_level}: ${(point.attack_probability*100).toFixed(0)}%`}><i/><strong>{(point.attack_probability*100).toFixed(0)}%</strong><span>{point.risk_level}</span></div>)}</div> : <div className="empty-state">No risk history recorded.</div>}</article>
}
