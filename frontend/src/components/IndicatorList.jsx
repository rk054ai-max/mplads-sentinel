import React from 'react'

export default function IndicatorList({components, limit=5}){
  const items = React.useMemo(()=>{
    if(!components) return []
    // flatten component evidence into indicators with score and short reason
    const indicators = Object.entries(components).flatMap(([k,v])=>{
      const reasons = v.evidence || []
      const primary = reasons.length? reasons[0] : ''
      return [{component: k, score: v.score, reason: primary}]
    })
    indicators.sort((a,b)=> (b.score||0)-(a.score||0))
    return indicators.slice(0,limit)
  },[components,limit])

  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Why flagged</h3>
      <ul className="list-disc list-inside">
        {items.map((it,idx)=> (
          <li key={idx} className="mb-1"><strong className="capitalize">{it.component}</strong>: {it.reason || 'Indicator present'} <span className="text-sm text-slate-500">({it.score})</span></li>
        ))}
      </ul>
    </div>
  )
}
