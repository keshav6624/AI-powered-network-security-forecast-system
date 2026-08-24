const metrics = [
  { key: 'active_hosts', label: 'Active nodes', suffix: '', hint: 'reachable' },
  { key: 'network_flows', label: 'Flows inspected', suffix: '', hint: 'total windows' },
  { key: 'anomalies', label: 'Anomalies', suffix: '', hint: 'requires review', tone: 'warn' },
  { key: 'current_risk', label: 'Risk index', suffix: '/100', hint: 'current posture', tone: 'danger' },
  { key: 'attack_probability', label: 'Attack likelihood', suffix: '%', hint: 'next 5 minutes', probability: true, tone: 'signal' },
]

export default function KpiCards({ kpis }) {
  if (!kpis) return null
  return <section className="kpi-strip" aria-label="Operational summary">{metrics.map(metric => {
    const raw = kpis[metric.key] ?? 0
    const value = metric.probability ? (raw * 100).toFixed(1) : Number(raw).toLocaleString()
    return <article className={`kpi-cell ${metric.tone || ''}`} key={metric.key}><div className="kpi-label">{metric.label}</div><div className="kpi-value data">{value}<small>{metric.suffix}</small></div><div className="kpi-hint">{metric.hint}</div></article>
  })}</section>
}
