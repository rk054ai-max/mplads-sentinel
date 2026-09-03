import React from 'react'

function haversine(a,b){
  if(!a||!b) return null
  const toRad = (v)=> v * Math.PI/180
  const R = 6371
  const dLat = toRad(b.latitude - a.latitude)
  const dLon = toRad(b.longitude - a.longitude)
  const lat1 = toRad(a.latitude)
  const lat2 = toRad(b.latitude)
  const h = Math.sin(dLat/2)**2 + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2
  return 2*R*Math.asin(Math.sqrt(h))
}

export default function DuplicatePanel({work, allWorks}){
  const candidates = (allWorks||[]).filter(w=>w.work_id !== work.work_id && w.description && work.description && w.description.toLowerCase().includes(work.description.toLowerCase().slice(0,20)))
  const rows = candidates.map(c=>({
    work_id: c.work_id,
    similarity: Math.min(100, Math.round((c.description && work.description && c.description===work.description)? 100 : 50)),
    distance_km: (c.latitude && c.longitude && work.latitude && work.longitude) ? Number(haversine({latitude:work.latitude, longitude:work.longitude},{latitude:c.latitude, longitude:c.longitude}).toFixed(2)) : null
  }))

  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Duplicate analysis</h3>
      {rows.length? <table className="w-full text-sm"><thead><tr className="text-slate-500"><th>Work</th><th>Similarity</th><th>Distance (km)</th></tr></thead><tbody>{rows.map(r=>(<tr key={r.work_id} className="border-t"><td>{r.work_id}</td><td>{r.similarity}%</td><td>{r.distance_km ?? '-'}</td></tr>))}</tbody></table> : <div className="text-sm text-slate-500">No similar works detected</div>}
    </div>
  )
}
