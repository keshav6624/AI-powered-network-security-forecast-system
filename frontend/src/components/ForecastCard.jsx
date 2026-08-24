const riskTone = level => level === 'CRITICAL' || level === 'HIGH' ? 'danger' : level === 'MEDIUM' ? 'warn' : 'safe'

export default function ForecastCard({ forecast }) {
  if (!forecast) return null
  const pct = Math.round(forecast.attack_probability * 100)
  const angle = Math.max(8, pct * 3.6)
  return (
    <article className="panel forecast-panel">
      <div className="panel-head"><h1 className="panel-title">Threat aperture</h1><span className={`status-pill ${riskTone(forecast.risk_level)}`}>{forecast.risk_level} risk</span></div>
      <div className="forecast-body">
        <div className="aperture" style={{'--risk-angle': `${angle}deg`}} aria-label={`${pct}% attack probability`}>
          <div className="aperture-scan" />
          <div className="aperture-core"><span className="data">{pct}</span><small>%</small></div>
        </div>
        <div className="forecast-copy"><span className="forecast-eyebrow mono">Projected / T+{forecast.horizon_minutes} min</span><h2 className="display">Attack likelihood is <em>{pct > 60 ? 'elevated' : pct > 30 ? 'developing' : 'contained'}</em></h2><p>The ensemble is tracking temporal drift across recent network windows.</p><div className="forecast-facts"><div><span>Risk index</span><strong className="data">{forecast.risk_score}/100</strong></div><div><span>Trajectory</span><strong>{forecast.trend || 'Stable'}</strong></div></div></div>
      </div>
    </article>
  )
}
