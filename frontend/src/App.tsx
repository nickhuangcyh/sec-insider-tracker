import { useState, useEffect } from 'react'
import { fetchIndex, fetchDateData, fetchMultipleDates } from './api'
import { Transaction } from './types'
import TransactionTable from './components/TransactionTable'

type Tab = 'latest' | 'topInsider' | 'topOwner'

export default function App() {
  const [tab, setTab] = useState<Tab>('latest')
  const [dates, setDates] = useState<string[]>([])
  const [selectedDate, setSelectedDate] = useState('')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  // Load index on mount
  useEffect(() => {
    fetchIndex().then((d) => {
      setDates(d)
      if (d.length) setSelectedDate(d[0])
    }).catch(console.error)
  }, [])

  // Load data when tab or selectedDate changes
  useEffect(() => {
    if (!dates.length) return
    setLoading(true)

    if (tab === 'latest') {
      if (!selectedDate) return
      fetchDateData(selectedDate)
        .then((d) => setTransactions(d.transactions))
        .catch(console.error)
        .finally(() => setLoading(false))
    } else {
      const recentDates = dates.slice(0, 7)
      fetchMultipleDates(recentDates)
        .then((results) => {
          let all = results.flatMap((r) => r.transactions)
          if (tab === 'topOwner') {
            all = all.filter((t) => t.relationship?.includes('10% Owner'))
          }
          all.sort((a, b) => b.value - a.value)
          setTransactions(all)
        })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [tab, selectedDate, dates])

  const tabs: { key: Tab; label: string }[] = [
    { key: 'latest', label: 'Latest Insider Trading' },
    { key: 'topInsider', label: 'Top Insider Trading Recent Week' },
    { key: 'topOwner', label: 'Top 10% Owner Trading Recent Week' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-4">🚀 SEC Insider Tracker</h1>

      {/* Tab Bar */}
      <div className="flex items-center gap-1 mb-4 border-b border-gray-300 pb-2 flex-wrap">
        {tabs.map((t, i) => (
          <span key={t.key}>
            {i > 0 && <span className="text-gray-400 mx-1">|</span>}
            <button
              onClick={() => setTab(t.key)}
              className={`px-1 ${tab === t.key ? 'font-bold text-black' : 'text-blue-600 hover:underline'}`}
            >
              {t.label}
            </button>
          </span>
        ))}

        {/* Date selector for latest tab */}
        {tab === 'latest' && dates.length > 0 && (
          <select
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="ml-auto border border-gray-300 rounded px-2 py-1 text-sm"
          >
            {dates.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <p className="text-center py-8 text-gray-500">Loading...</p>
      ) : (
        <TransactionTable transactions={transactions} />
      )}
    </div>
  )
}
