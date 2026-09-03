import React from 'react'

export default function VerificationChecklist({recommendations=[], work}){
  const base = [
    'Verify sanction paperwork and approvals',
    'Confirm invoices and supplier contracts',
    'Cross-check site visit / photo evidence',
    'Request bank/payment records for disbursements',
  ]
  const items = [...(recommendations || []), ...base]
  return (
    <div className="card">
      <h3 className="font-semibold mb-2">Recommended verification</h3>
      <ol className="list-decimal list-inside text-sm">
        {items.map((it,i)=>(<li key={i}>{it}</li>))}
      </ol>
      <div className="mt-3 text-xs text-slate-500">Risk indicators are intended to prioritize administrative verification and do not establish fraud or wrongdoing.</div>
    </div>
  )
}
