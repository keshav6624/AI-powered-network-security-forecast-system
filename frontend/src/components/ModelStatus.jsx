const roles = { logistic_regression:'Baseline classifier', xgboost:'Tabular classifier', lstm:'Sequence model', transformer:'Attention model', isolation_forest:'Anomaly detector' }

export default function ModelStatus({ models }) {
  return <article className="panel" id="model-status" tabIndex="-1"><div className="panel-head"><h2 className="panel-title">Model health</h2><span className="panel-meta">Runtime registry</span></div><div className="model-status-list">{(models || []).map(model => { const healthy=model.available;const status=model.status || (model.demo?'Demo':healthy?'Available':'Offline');return <div className="model-status-row" key={model.model}><div><strong>{model.display_name}</strong><small>{roles[model.model] || 'Forecast model'}</small></div><span className={`status-pill ${healthy?'safe':'danger'}`}>{status}</span></div>})}</div></article>
}
