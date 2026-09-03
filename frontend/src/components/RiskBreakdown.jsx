import React from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#10b981','#f59e0b','#ef4444']

export default function RiskBreakdown({distribution}){
  const data = [
    {name:'LOW', value: distribution?.LOW||0},
    {name:'MEDIUM', value: distribution?.MEDIUM||0},
    {name:'HIGH', value: distribution?.HIGH||0},
  ]
  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-2">Risk Distribution</h3>
      <div style={{height:220}}>
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} dataKey="value" innerRadius={40} outerRadius={80} label />
            {data.map((entry, index)=>(<Cell key={index} fill={COLORS[index%COLORS.length]} />))}
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
