import { useState, useRef, useEffect } from 'react'

const ALL_TYPES = ['Purchase', 'Sale', 'Grant', 'Exercise', 'Tax Withholding', 'Gift', 'Disposition', 'Conversion']

export default function TransactionFilter({ selectedTypes, onChange }: { selectedTypes: Set<string>; onChange: (types: Set<string>) => void }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const label = selectedTypes.size <= 2
    ? `Filter: ${[...selectedTypes].join(', ') || 'None'}`
    : `Filter: ${selectedTypes.size} selected`

  const toggle = (type: string) => {
    const next = new Set(selectedTypes)
    next.has(type) ? next.delete(type) : next.add(type)
    onChange(next)
  }

  return (
    <div ref={ref} className="relative">
      <button onClick={() => setOpen(!open)} className="border border-gray-300 rounded px-2 py-1 text-sm hover:bg-gray-50">
        {label}
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 bg-white border border-gray-300 rounded shadow-lg z-10 py-1 min-w-[180px]">
          {ALL_TYPES.map((type) => (
            <label key={type} className="flex items-center gap-2 px-3 py-1 hover:bg-gray-50 cursor-pointer text-sm">
              <input type="checkbox" checked={selectedTypes.has(type)} onChange={() => toggle(type)} />
              {type}
            </label>
          ))}
        </div>
      )}
    </div>
  )
}
