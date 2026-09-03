import React from 'react'

function daysBetween(a,b){
  if(!a || !b) return null
  const da = new Date(a)
  const db = new Date(b)
  return Math.round((db - da)/(1000*60*60*24))
}

export default function CompliancePanel({work, component}){
  const sanctionDelay = work?.recommendation_date && work?.sanction_date ? daysBetween(work.recommendation_date, work.sanction_date) : null
  const paymentDelay = work?.sanction_date && work?.start_date ? daysBetween(work.sanction_date, work.start_date) : null
  const completionDelay = work?.start_date && work?.completion_date ? daysBetween(work.start_date, work.completion_date) : null

  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Compliance</h3>
      <div className="text-sm text-slate-600 mb-2">Triggered rules</div>
      <ul className="list-disc list-inside text-sm mb-3">
        {(component?.evidence||[]).map((e,i)=>(<li key={i}>{e}</li>))}
      </ul>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <div className="text-slate-500">Sanction delay (days)</div>
          <div className="font-semibold">{sanctionDelay ?? '-'}</div>
        </div>
        <div>
          <div className="text-slate-500">Payment delay (days)</div>
          <div className="font-semibold">{paymentDelay ?? '-'}</div>
        </div>
        <div>
          <div className="text-slate-500">Completion delay (days)</div>
          <div className="font-semibold">{completionDelay ?? '-'}</div>
        </div>
        <div>
          <div className="text-slate-500">Compliance score</div>
          <div className="font-semibold">{component?.score ?? '-'}</div>
        </div>
      </div>
    </div>
  )
}
