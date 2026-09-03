import React from 'react'
import RiskBadge from '../components/RiskBadge'
import IndicatorList from '../components/IndicatorList'
import FinancialPanel from '../components/FinancialPanel'
import CompliancePanel from '../components/CompliancePanel'
import DuplicatePanel from '../components/DuplicatePanel'
import VerificationChecklist from '../components/VerificationChecklist'
import MapPanel from '../components/MapPanel'

export default function Investigation({workId}){
  const [data,setData]=React.useState(null)
  const [allWorks,setAllWorks]=React.useState([])

  React.useEffect(()=>{
    // load mock analysis and work data; prefer API but fallback to public files
    fetch('/api/work/'+workId).then(r=>{ if(r.ok) return r.json(); throw new Error('api') }).then(setData).catch(()=>{
      Promise.all([fetch('/public/mock_analysis.json').then(r=>r.json()).catch(()=>[]), fetch('/data/mock/sample_work.json').then(r=>r.json()).catch(()=>[])]).then(([analysis, works])=>{
        const a = (analysis||[]).find(x=>x.work_id===workId)
        const w = (works||[]).find(x=>x.work_id===workId)
        setData({work: w, analysis: a})
        setAllWorks(works||[])
      })
    })
    // also try to load all works via API
    fetch('/api/v1/works').then(r=>r.json()).then(d=>{ setAllWorks(d.items||[]) }).catch(()=>{})
  },[workId])

  if(!data || !data.work) return <div className="container">Loading...</div>

  const work = data.work
  const analysis = data.analysis || { components: {} }

  return (
    <div>
      <div className="header"><div className="container"><h1 className="text-2xl">Investigation</h1></div></div>

      <div className="container grid grid-cols-3 gap-6">
        {/* HEADER */}
        <div className="col-span-2">
          <div className="card mb-4">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm text-slate-500">Work ID</div>
                <div className="text-lg font-semibold">{work.work_id}</div>
                <div className="text-sm text-slate-600 mt-2">{work.description}</div>
                <div className="text-sm text-slate-500 mt-1">{work.district} • {work.state} — {work.status}</div>
              </div>

              <div className="text-right">
                <div className="text-6xl font-bold">{analysis.risk_score ?? 'N/A'}</div>
                <div className="mt-2"><RiskBadge level={analysis.risk_level} /></div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-1"><IndicatorList components={analysis.components} limit={5} /></div>
            <div className="col-span-2"><FinancialPanel work={work} allWorks={allWorks} component={analysis.components?.financial} /></div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="col-span-1"><CompliancePanel work={work} component={analysis.components?.compliance} /></div>
            <div className="col-span-1"><DuplicatePanel work={work} allWorks={allWorks} /></div>
            <div className="col-span-1"><VerificationChecklist recommendations={analysis.recommendations} work={work} /></div>
          </div>

        </div>

        {/* MAP & AI summary */}
        <div>
          <MapPanel selectedWork={work} nearby={allWorks.filter(w=>w.work_id!==work.work_id)} assets={[]} height={420} />
          <div className="mt-4 card"><h3 className="font-semibold">AI Summary</h3><p className="mt-2 text-sm">{analysis.ai_summary || 'No summary available'}</p></div>
        </div>
      </div>
    </div>
  )
}
