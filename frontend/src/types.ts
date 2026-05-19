export interface Transaction {
  ticker: string
  company: string
  insider: string
  relationship: string
  title: string
  date: string
  type: string
  transaction: string
  shares: number
  price: number
  value: number
  shares_total: number | null
  url: string
}

export interface DateData {
  date: string
  transactions: Transaction[]
}
