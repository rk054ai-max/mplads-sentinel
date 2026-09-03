import React from 'react'

export default function Timeline({items=[]}){
  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Timeline</h3>
      <ol className="list-decimal list-inside text-sm">
        {items.length? items.map((it,i)=>(<li key={i}>{it}</li>)) : <li>No timeline entries</li>}
      </ol>
    </div>
  )
}
