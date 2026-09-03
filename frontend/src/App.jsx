import React from 'react'
import Dashboard from './pages/Dashboard'
import Investigation from './pages/Investigation'

export default function App(){
  const [route, setRoute] = React.useState(window.location.hash.replace('#','') || '/dashboard')

  React.useEffect(()=>{
    const onHash = ()=> setRoute(window.location.hash.replace('#','') || '/dashboard')
    window.addEventListener('hashchange', onHash)
    return ()=> window.removeEventListener('hashchange', onHash)
  },[])

  if(route.startsWith('/work/')){
    const id = route.split('/')[2]
    return <Investigation workId={id} />
  }
  return <Dashboard />
}
