import React from 'react'
import KPICard from '../components/KPICard'
import RiskBreakdown from '../components/RiskBreakdown'
import WorkTable from '../components/WorkTable'
import MapPanel from '../components/MapPanel'

export default function Dashboard(){
  const [summary,setSummary]=React.useState(null)
  const [works,setWorks]=React.useState([])

  React.useEffect(()=>{
    // Use local mock when available
    fetch('/public/mock_analysis.json').catch(()=>fetch('/mock_analysis.json')).then(()=>{}).catch(()=>{})
    fetch('/api/v1/summary').then(r=>r.json()).then(setSummary).catch(()=>{
      // fallback: generate from public/mock_analysis.json and data/mock/sample_work.json
      Promise.all([fetch('/public/mock_analysis.json').then(r=>r.json()).catch(()=>[]), fetch('/data/mock/sample_work.json').then(r=>r.json()).catch(()=>[])]).then(([analysis, worksData])=>{
        const analysisMap = Object.fromEntries((analysis||[]).map(a=>[a.work_id,a]))
        setWorks((worksData||[]).map(w=>({work_id:w.work_id||w.work_id, sanctioned_amount:w.sanctioned_amount, expenditure:w.expenditure, risk_level: analysisMap[w.work_id]?.risk_level})))
        const dist = {LOW:0,MEDIUM:0,HIGH:0}
        (analysis||[]).forEach(a=>{ if(dist[a.risk_level]!==undefined) dist[a.risk_level]+=1 })
        setSummary({total_works:(worksData||[]).length, total_expenditure: (worksData||[]).reduce((s,w)=>s+Number(w.expenditure||0),0), completed_works: (worksData||[]).filter(w=>w.status==='completed').length, delayed_works:(worksData||[]).filter(w=>w.status==='delayed').length, high_risk_works:(analysis||[]).filter(a=>a.risk_level==='HIGH').length, risk_distribution: dist})
      })
    })
    fetch('/api/v1/works').then(r=>r.json()).then(d=>setWorks(d.items)).catch(()=>{})
  },[])

  return (
    <div>
      <div className="header"><div className="container"><h1 className="text-2xl">MPLADS Sentinel — Dashboard</h1></div></div>
      <div className="container">
        <div className="grid grid-cols-3 gap-4 mb-4">
          <KPICard label="Total works" value={summary?summary.total_works:'-'} />
          <KPICard label="Total expenditure" value={summary?summary.total_expenditure:'-'} />
          <KPICard label="Completed works" value={summary?summary.completed_works:'-'} />
          <KPICard label="Delayed works" value={summary?summary.delayed_works:'-'} />
          <KPICard label="High risk works" value={summary?summary.high_risk_works:'-'} className="col-span-2" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <RiskBreakdown distribution={summary?summary.risk_distribution:{LOW:0,MEDIUM:0,HIGH:0}} />
          <div>
            <WorkTable works={(works||[]).filter(w=>w.risk_level==='HIGH')} onSelect={(id)=> window.location.hash = '#/work/'+id} />
            <div className="mt-4"><MapPanel /></div>
          </div>
        </div>
      </div>
    </div>
  )
}
