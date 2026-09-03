import React from 'react'

export default function FinancialPanel({work, allWorks, component}){
  const sanctioned = Number(work?.sanctioned_amount||0)
  const expenditure = Number(work?.expenditure||0)
  const peerWorks = (allWorks||[]).filter(w=> w.work_type === work.work_type && w.work_id !== work.work_id)
  const peerAvg = peerWorks.length? peerWorks.reduce((s,w)=>s + Number(w.expenditure||0),0)/peerWorks.length : 0
  const deviation = peerAvg? ((expenditure - peerAvg)/peerAvg)*100 : null

  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Financial</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-slate-500">Observed cost</div>
          <div className="text-lg font-semibold">{expenditure || 'N/A'}</div>
        </div>
        <div>
          <div className="text-sm text-slate-500">Peer benchmark</div>
          <div className="text-lg font-semibold">{peerAvg ? peerAvg.toFixed(2) : 'N/A'}</div>
        </div>
        <div>
          <div className="text-sm text-slate-500">Deviation</div>
          <div className="text-lg">{deviation===null? 'N/A' : deviation.toFixed(1)+'%'}</div>
        </div>
        <div>
          <div className="text-sm text-slate-500">Financial score</div>
          <div className="text-lg font-semibold">{component?.score ?? 'N/A'}</div>
        </div>
      </div>
    </div>
  )
}
