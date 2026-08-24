import Header from '../components/Header.jsx'
import KpiCards from '../components/KpiCards.jsx'
import ForecastCard from '../components/ForecastCard.jsx'
import TrafficChart from '../components/TrafficChart.jsx'
import RiskTimeline from '../components/RiskTimeline.jsx'
import ModelComparison from '../components/ModelComparison.jsx'
import NetworkTopology from '../components/NetworkTopology.jsx'
import Explainability from '../components/Explainability.jsx'
import AlertsPanel from '../components/AlertsPanel.jsx'
import ReplayControls from '../components/ReplayControls.jsx'
import ModelStatus from '../components/ModelStatus.jsx'
import { useDashboardData } from '../hooks/useDashboardData.js'
import { useIncidentActions } from '../hooks/useIncidentActions.js'
import { useReplayActions } from '../hooks/useReplayActions.js'

export default function Dashboard() {
  const { data, setData, replay, error, setError, load } = useDashboardData()
  const replayActions = useReplayActions({ reload: load, onError: setError })
  const incidentActions = useIncidentActions({ setData, reload: load })

  if (error) {
    return (
      <div className="error-screen">
        <section className="panel error-card" role="alert">
          <span className="status-pill danger">Connection interrupted</span>
          <h1>Telemetry link is offline</h1>
          <p>{error}</p>
          <button className="action primary" onClick={load}>Retry connection</button>
        </section>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="loading-screen">
        <div>
          <div className="loading-mark">NG</div>
          <p className="panel-meta" style={{ marginTop: 18 }}>Establishing telemetry link</p>
        </div>
      </div>
    )
  }

  const latest = replay?.last_prediction
  const probability = data.forecast.attack_probability
  const modelProbabilities = latest?.models || {
    logistic_regression: Math.min(1, probability * 0.92),
    xgboost: Math.min(1, probability * 0.97),
    lstm: Math.min(1, probability * 1.02),
    transformer: Math.min(1, probability * 1.05),
  }

  return (
    <div className="app-shell">
      <a href="#main-dashboard" className="sr-only focus:not-sr-only">Skip to dashboard</a>
      <Header
        demoMode={data.demo_mode}
        systemStatus={data.system_status}
        timestamp={data.timestamp}
      />

      <main id="main-dashboard" className="dashboard-main">
        <KpiCards kpis={data.kpis} />

        <section className="command-grid" aria-label="Forecast command center">
          <ForecastCard forecast={data.forecast} />
          <TrafficChart history={data.risk_timeline} live={replay?.running} />
        </section>

        <section className="analysis-grid" aria-label="Threat analysis">
          <NetworkTopology graph={data.network_graph} />
          <div className="stack">
            <ModelComparison models={modelProbabilities} />
            <ModelStatus models={data.models_status} />
          </div>
          <div className="stack">
            <RiskTimeline history={data.risk_timeline} />
            <Explainability
              explanations={latest?.explanations || [
                'Packet length variance elevated',
                'Connection rate is above baseline',
              ]}
              demoMode={data.demo_mode}
            />
          </div>
        </section>

        <section className="response-grid" aria-label="Response operations">
          <AlertsPanel
            alerts={data.recent_alerts}
            onAck={incidentActions.acknowledge}
            onResolve={incidentActions.resolve}
            action={incidentActions.action}
            feedback={incidentActions.feedback}
          />
          <ReplayControls
            status={replay}
            busyAction={replayActions.busyAction}
            onStart={replayActions.start}
            onStop={replayActions.stop}
            onReset={replayActions.reset}
            onStep={replayActions.step}
            onSpeed={replayActions.setSpeed}
          />
        </section>

        <footer className="dashboard-footer">
          <span>
            NetGuard AI / SIH26153 / Forecast horizon {data.forecast.horizon_minutes} minutes
          </span>
          <span>
            {data.demo_mode ? 'Simulation environment' : 'Production telemetry'} ·{' '}
            <a href="/docs" target="_blank" rel="noreferrer">API reference</a>
          </span>
        </footer>
      </main>
    </div>
  )
}
