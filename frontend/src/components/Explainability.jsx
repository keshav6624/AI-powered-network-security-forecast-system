export default function Explainability({ explanations, demoMode }) {
  const reasons = (explanations || []).map(reason => reason.replace(/^[↑→✓]\s*/, ''))
  return <article className="panel"><div className="panel-head"><h2 className="panel-title">Contributing signals</h2>{demoMode && <span className="status-pill warn">Simulated</span>}</div><div className="explanation-list">{reasons.length ? reasons.map((reason,index) => <div className="explanation-item" key={`${reason}-${index}`}><span className="explanation-index">0{index+1}</span><span>{reason}</span></div>) : <div className="empty-state">No contributing signals found.</div>}</div></article>
}
