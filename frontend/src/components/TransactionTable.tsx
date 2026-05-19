import { useState } from 'react'
import { Transaction } from '../types'

const TRANSACTION_COLORS: Record<string, string> = {
  Purchase: 'text-green-700 font-semibold',
  Sale: 'text-red-700 font-semibold',
  Exercise: 'text-purple-700 font-semibold',
  Grant: 'text-blue-700 font-semibold',
  'Tax Withholding': 'text-yellow-700 font-semibold',
}

function formatCurrency(n: number): string {
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatInt(n: number | null): string {
  if (n === null || n === undefined) return ''
  return n.toLocaleString('en-US')
}

export default function TransactionTable({ transactions }: { transactions: Transaction[] }) {
  const [sortDir, setSortDir] = useState<'asc' | 'desc' | null>(null)

  if (!transactions.length) {
    return <p className="text-center py-8 text-gray-500">No transactions found.</p>
  }

  const sorted = sortDir
    ? [...transactions].sort((a, b) => sortDir === 'desc' ? b.value - a.value : a.value - b.value)
    : transactions

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100 border-b border-gray-300">
            <th className="px-3 py-2 text-left font-semibold">Ticker</th>
            <th className="px-3 py-2 text-left font-semibold">Owner</th>
            <th className="px-3 py-2 text-left font-semibold">Relationship</th>
            <th className="px-3 py-2 text-left font-semibold">Date</th>
            <th className="px-3 py-2 text-left font-semibold">Transaction</th>
            <th className="px-3 py-2 text-right font-semibold">Cost</th>
            <th className="px-3 py-2 text-right font-semibold">#Shares</th>
            <th
              className="px-3 py-2 text-right font-semibold cursor-pointer select-none hover:text-blue-600"
              onClick={() => setSortDir(d => d === 'desc' ? 'asc' : 'desc')}
            >
              Value ($) {sortDir === 'desc' ? '▼' : sortDir === 'asc' ? '▲' : '⇅'}
            </th>
            <th className="px-3 py-2 text-right font-semibold">#Shares Total</th>
            <th className="px-3 py-2 text-center font-semibold">SEC Form 4</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((tx, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              <td className="px-3 py-1.5 font-medium">{tx.ticker}</td>
              <td className="px-3 py-1.5">{tx.insider}</td>
              <td className="px-3 py-1.5">{tx.relationship}</td>
              <td className="px-3 py-1.5">{tx.date}</td>
              <td className={`px-3 py-1.5 ${TRANSACTION_COLORS[tx.transaction] || ''}`}>
                {tx.transaction}
              </td>
              <td className="px-3 py-1.5 text-right font-mono">{formatCurrency(tx.price)}</td>
              <td className="px-3 py-1.5 text-right font-mono">{formatInt(tx.shares)}</td>
              <td className="px-3 py-1.5 text-right font-mono">{formatInt(tx.value)}</td>
              <td className="px-3 py-1.5 text-right font-mono">{formatInt(tx.shares_total)}</td>
              <td className="px-3 py-1.5 text-center">
                <a href={tx.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  Link
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
