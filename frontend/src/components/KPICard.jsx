import React from 'react'

export default function KPICard({label, value, className}){
  return (
    <div className={`p-4 rounded-md shadow-sm bg-white ${className||''}`}>
      <div className="text-sm text-slate-500">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  )
}
