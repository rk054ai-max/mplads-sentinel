const e = React.createElement;

function App() {
  const [view, setView] = React.useState(window.location.hash.replace('#','') || '/');

  React.useEffect(() => {
    function onHash() { setView(window.location.hash.replace('#','') || '/'); }
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  if (view === '/' || view === '/dashboard') {
    return e(Dashboard, {});
  }
  if (view.startsWith('/work/')) {
    const workId = view.split('/')[2];
    return e(Investigation, { workId });
  }
  return e('div', null, 'Not found');
}

function Dashboard() {
  const [summary, setSummary] = React.useState(null);
  const [works, setWorks] = React.useState([]);

  React.useEffect(() => {
    fetch('/api/v1/summary').then(r=>r.json()).then(setSummary).catch(()=>{});
    fetch('/api/v1/works').then(r=>r.json()).then(d=>setWorks(d.items)).catch(()=>{});
  }, []);

  React.useEffect(()=>{
    // init map after works loaded
    if (works.length>0) {
      const map = L.map('map').setView([20.0,78.0], 5);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
      works.forEach(w=>{ if(w.latitude && w.longitude) { L.circleMarker([w.latitude,w.longitude]).addTo(map).bindPopup(w.work_id+' - '+(w.risk_level||'N/A')); } });
    }
  }, [works]);

  return e('div', null, [
    e('div', {className:'header', key:'h'}, e('h1', null, 'MPLADS Sentinel — Dashboard')),
    e('div', {className:'container', key:'c'}, [
      e('div', {className:'cards', key:'cards'}, [
        e('div', {className:'card', key:'c1'}, e('div', null, [e('div', {className:'small'}, 'Total works'), e('div', {style:{fontSize:24}}, summary?summary.total_works:'-')])),
        e('div', {className:'card', key:'c2'}, e('div', null, [e('div', {className:'small'}, 'Total expenditure'), e('div', {style:{fontSize:24}}, summary?summary.total_expenditure:'-')])),
        e('div', {className:'card', key:'c3'}, e('div', null, [e('div', {className:'small'}, 'Completed works'), e('div', {style:{fontSize:24}}, summary?summary.completed_works:'-')])),
        e('div', {className:'card', key:'c4'}, e('div', null, [e('div', {className:'small'}, 'Delayed works'), e('div', {style:{fontSize:24}}, summary?summary.delayed_works:'-')])),
        e('div', {className:'card', key:'c5'}, e('div', null, [e('div', {className:'small'}, 'High risk works'), e('div', {style:{fontSize:24}, className:'high-risk'}, summary?summary.high_risk_works:'-')])),
      ]),

      e('div', {className:'grid', key:'grid'}, [
        e('div', {key:'left'}, [
          e('div', {className:'card', key:'risk'}, [e('h3', null, 'Risk Distribution'), e('pre', null, summary?JSON.stringify(summary.risk_distribution,null,2):'Loading...')]),
          e('div', {className:'card', key:'mapcard'}, [e('h3', null, 'Map'), e('div', {id:'map', className:'map'})]),
        ]),
        e('div', {key:'right'}, [
          e('div', {className:'table', key:'table'}, [e('h3', null, 'High Risk Works'), e('ul', null, works.filter(w=>w.risk_level==='HIGH').map(w=>e('li', {key:w.work_id}, e('a', {href:'#/work/'+w.work_id}, w.work_id+' — '+(w.sanctioned_amount||'')+' | '+(w.expenditure||'')))))])
        ])
      ])
    ])
  ]);
}

function Investigation({workId}){
  const [data, setData] = React.useState(null);

  React.useEffect(()=>{
    fetch('/api/v1/works/'+workId).then(r=>r.json()).then(setData).catch(()=>{});
  },[workId]);

  React.useEffect(()=>{
    if(data && data.work && data.work.latitude && data.work.longitude){
      const map = L.map('imap').setView([data.work.latitude, data.work.longitude], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
      L.marker([data.work.latitude, data.work.longitude]).addTo(map);
    }
  },[data]);

  if(!data) return e('div', null, 'Loading...');
  const analysis = data.analysis;

  return e('div', null, [
    e('div', {className:'header'}, e('h1', null, 'Investigation — '+workId)),
    e('div', {className:'container'}, [
      e('div', {className:'card'}, [
        e('h2', null, 'Risk'),
        e('div', null, [e('div', null, 'Score: '+(analysis?analysis.risk_score:'N/A')), e('div', null, 'Level: '+(analysis?analysis.risk_level:'N/A'))])
      ]),

      e('div', {className:'grid'}, [
        e('div', {key:'left'}, [
          e('div', {className:'card'}, [
            e('h3', null, 'Component Evidence'),
            analysis?Object.entries(analysis.components).map(([k,v])=>e('div',{key:k, style:{marginBottom:8}}, [e('strong', null, k), e('div', null, 'Score: '+v.score), e('ul', null, v.evidence.map((it,idx)=>e('li',{key:idx}, it)))])):'No analysis available'
          ]),

          e('div', {className:'card'}, [e('h3', null, 'Recommendations'), e('ul', null, analysis?analysis.recommendations.map((r,idx)=>e('li',{key:idx}, r)):'-')]),

          e('div', {className:'card'}, [e('h3', null, 'AI Summary'), e('p', null, analysis?analysis.ai_summary:'-')])
        ]),
        e('div', {key:'right'}, [
          e('div', {className:'card'}, [e('h3', null, 'Map'), e('div', {id:'imap', className:'map'})])
        ])
      ])
    ])
  ]);
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
