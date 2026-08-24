import { useEffect, useState } from 'react'

const sections = [
  { id: 'main-dashboard', label: 'Operations' },
  { id: 'alerts-panel', label: 'Incidents' },
  { id: 'model-status', label: 'Models' },
]

function Mark() {
  return <svg aria-hidden="true" viewBox="0 0 32 32" width="30" height="30"><path d="M16 2 28 8v8c0 7.5-5 11.8-12 14C9 27.8 4 23.5 4 16V8l12-6Z" fill="none" stroke="currentColor" strokeWidth="1.5"/><path d="m10 17 4 4 8-10" fill="none" stroke="currentColor" strokeWidth="1.8"/></svg>
}

export default function Header({ demoMode, systemStatus, timestamp }) {
  const [activeSection, setActiveSection] = useState('main-dashboard')
  const observedAt = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'

  useEffect(() => {
    const updateActiveSection = () => {
      const offset = 110
      const current = sections
        .map(section => ({ id: section.id, top: document.getElementById(section.id)?.getBoundingClientRect().top }))
        .filter(section => section.top != null && section.top <= offset)
        .sort((a, b) => b.top - a.top)[0]
      setActiveSection(current?.id || sections[0].id)
    }
    updateActiveSection()
    window.addEventListener('scroll', updateActiveSection, { passive: true })
    return () => window.removeEventListener('scroll', updateActiveSection)
  }, [])

  const navigateTo = id => {
    const target = document.getElementById(id)
    if (!target) return
    setActiveSection(id)
    target.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })
    window.history.replaceState(null, '', `#${id}`)
  }

  return (
    <header className="command-header">
      <div className="command-header__inner">
        <div className="brand-lockup"><span className="brand-mark"><Mark /></span><div><div className="brand-name display">NETGUARD</div><div className="brand-sub mono">Predictive defense network</div></div></div>
        <nav className="header-nav" aria-label="Dashboard sections">{sections.map(section => <button type="button" key={section.id} className={activeSection === section.id ? 'active' : ''} aria-current={activeSection === section.id ? 'page' : undefined} onClick={() => navigateTo(section.id)}>{section.label}</button>)}</nav>
        <div className="header-state"><div className="header-clock"><span>Last telemetry</span><strong className="data">{observedAt}</strong></div>{demoMode && <span className="status-pill warn">Simulation</span>}<span className="status-pill safe">{systemStatus || 'Online'}</span></div>
      </div>
    </header>
  )
}
