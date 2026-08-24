export const pct = (v) => `${(v * 100).toFixed(1)}%`
export const riskColor = (level) => ({
  LOW: '#22c55e',
  MEDIUM: '#eab308',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
}[level] || '#64748b')

export const riskBg = (level) => ({
  LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  MEDIUM: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/30',
}[level] || 'bg-slate-700 text-slate-300')

export const timeAgo = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  const diff = (Date.now() - d.getTime()) / 1000
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`
  return d.toLocaleTimeString()
}
