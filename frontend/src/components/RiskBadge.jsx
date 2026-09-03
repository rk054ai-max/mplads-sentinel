import React from 'react'

const colorFor = (level)=>{
  if(level==='HIGH') return 'bg-red-600 text-white'
  if(level==='MEDIUM') return 'bg-yellow-500 text-black'
  return 'bg-green-600 text-white'
}

export default function RiskBadge({level}){
  return <span className={`px-3 py-1 rounded-full text-sm font-medium ${colorFor(level)}`}>{level||'N/A'}</span>
}
