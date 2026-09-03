import React from 'react'

export default function EvidenceCard({title, score, evidence=[]}){
  return (
    <div className="card">
      <div className="flex justify-between items-center"><h4 className="font-semibold">{title}</h4><div className="text-sm text-slate-500">Score: {score}</div></div>
      <ul className="mt-2 list-disc list-inside text-sm text-slate-700">
        {evidence.length? evidence.map((e,i)=>(<li key={i}>{e}</li>)) : <li>No evidence provided</li>}
      </ul>
    </div>
  )
}
