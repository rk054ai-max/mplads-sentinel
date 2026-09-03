import React from 'react'

export default function WorkTable({works=[], onSelect}){
  return (
    <div className="card">
      <h3 className="font-semibold mb-2">High Risk Works</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500"><th>Work ID</th><th>Sanctioned</th><th>Expenditure</th><th>Risk</th></tr>
        </thead>
        <tbody>
          {works.map(w=> (
            <tr key={w.work_id} className="border-t"><td><button className="text-sky-700" onClick={()=>onSelect?.(w.work_id)}>{w.work_id}</button></td><td>{w.sanctioned_amount}</td><td>{w.expenditure}</td><td>{w.risk_level||'N/A'}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
