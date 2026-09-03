import React from 'react'

export default function MapPanel({height=240, selectedWork=null, nearby=[], assets=[]}){
  const id = React.useMemo(()=>`map-${selectedWork?.work_id||Math.random().toString(36).slice(2,8)}`,[selectedWork])

  React.useEffect(()=>{
    if(typeof window === 'undefined' || !window.L) return
    const L = window.L
    const el = document.getElementById(id)
    if(!el) return
    // clear
    el.innerHTML = ''
    const map = L.map(el).setView([20.0,78.0], 5)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map)

    if(selectedWork && selectedWork.latitude && selectedWork.longitude){
      L.marker([selectedWork.latitude, selectedWork.longitude]).addTo(map).bindPopup(selectedWork.work_id)
      map.setView([selectedWork.latitude, selectedWork.longitude], 12)
    }
    nearby.forEach(w=>{ if(w.latitude && w.longitude){ L.circleMarker([w.latitude,w.longitude],{radius:6, color:'#f59e0b'}).addTo(map).bindPopup(w.work_id) }})
    assets.forEach(a=>{ if(a.latitude && a.longitude){ L.marker([a.latitude,a.longitude],{icon: L.icon({iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png', iconSize:[25,41]})}).addTo(map).bindPopup(a.name||'asset') }})

    return ()=>{ try{ map.remove() }catch(_){} }
  },[id, selectedWork, nearby, assets])

  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Spatial view</h3>
      <div id={id} style={{height}} className="rounded-md overflow-hidden" />
    </div>
  )
}
