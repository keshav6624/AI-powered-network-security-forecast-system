const names = { logistic_regression:'Logistic baseline', xgboost:'XGBoost', lstm:'Temporal LSTM', transformer:'Transformer' }

export default function ModelComparison({ models }) {
  const entries = Object.entries(names).map(([key,name]) => ({key,name,value:Number(models?.[key] || 0)}))
  const highest = Math.max(...entries.map(item => item.value))
  return <article className="panel"><div className="panel-head"><h2 className="panel-title">Ensemble consensus</h2><span className="panel-meta">4 predictors</span></div><div className="model-bars">{entries.map(item => <div className={`model-row ${item.value===highest?'best':''}`} key={item.key}><div className="model-row-head"><span>{item.name}</span><strong>{(item.value*100).toFixed(1)}%</strong></div><div className="model-track"><div className="model-fill" style={{width:`${Math.min(100,item.value*100)}%`}}/></div></div>)}</div></article>
}
