import { useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

function ThreatTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return <div className="custom-tooltip"><span>{point.fullTime}</span><strong>{point.probability}% likelihood</strong><span style={{marginTop: 5}}>{point.riskLevel} risk · index {point.riskScore}</span></div>
}

export default function TrafficChart({ history, live = false }) {
  const chartData = useMemo(() => (history || []).map((item, index) => {
    const timestamp = new Date(item.timestamp)
    const probability = Number(item.attack_probability) * 100
    return {
      id: `${item.timestamp}-${index}`,
      time: Number.isNaN(timestamp.getTime()) ? `W${index + 1}` : timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      fullTime: Number.isNaN(timestamp.getTime()) ? 'Unknown time' : timestamp.toLocaleString(),
      probability: Number.isFinite(probability) ? Number(Math.min(100, Math.max(0, probability)).toFixed(1)) : 0,
      riskLevel: item.risk_level || 'UNKNOWN',
      riskScore: item.risk_score ?? '—',
    }
  }), [history])

  const latest = chartData.at(-1)
  const pointStyle = chartData.length < 3 ? { r: 4, fill: '#070a0f', stroke: '#42d3e8', strokeWidth: 2 } : false

  return <article className="panel"><div className="panel-head"><div><h2 className="panel-title">Temporal threat signal</h2><div className="chart-legend" style={{marginTop: 8}}><span><i />Observed</span><span className="forecast"><i />Escalation line</span></div></div><div style={{display:'flex',alignItems:'center',gap:8}}>{live && <span className="status-pill signal">Live</span>}<span className="panel-meta">{latest ? `${latest.probability}% now` : 'No windows'}</span></div></div><div className="chart-body">{chartData.length ? <ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData} margin={{top: 10,right: 18,bottom: 4,left: 0}}><defs><linearGradient id="signalFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#42d3e8" stopOpacity=".28"/><stop offset="100%" stopColor="#42d3e8" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="#1b2a35" strokeDasharray="2 6" vertical={false}/><XAxis dataKey="time" tick={{fill:'#60747d',fontSize:9,fontFamily:'IBM Plex Mono'}} axisLine={false} tickLine={false} minTickGap={34}/><YAxis domain={[0,100]} ticks={[0,25,50,75,100]} tick={{fill:'#60747d',fontSize:9,fontFamily:'IBM Plex Mono'}} axisLine={false} tickLine={false} width={35}/><Tooltip content={<ThreatTooltip />} isAnimationActive={false}/><ReferenceLine y={60} stroke="#ff6469" strokeDasharray="5 5"/><Area type="monotone" dataKey="probability" stroke="#42d3e8" strokeWidth={2} fill="url(#signalFill)" dot={pointStyle} activeDot={{r:4,fill:'#070a0f',stroke:'#42d3e8',strokeWidth:2}} isAnimationActive={false} connectNulls/></AreaChart></ResponsiveContainer> : <div className="empty-state">Start replay to populate the temporal signal.</div>}</div></article>
}
