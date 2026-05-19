import { DateData } from './types'

const BASE = import.meta.env.BASE_URL + 'data'

export async function fetchIndex(): Promise<string[]> {
  const res = await fetch(`${BASE}/index.json`)
  if (!res.ok) throw new Error('Failed to fetch index')
  return res.json()
}

export async function fetchDateData(date: string): Promise<DateData> {
  const res = await fetch(`${BASE}/${date}.json`)
  if (!res.ok) throw new Error(`Failed to fetch data for ${date}`)
  return res.json()
}

export async function fetchMultipleDates(dates: string[]): Promise<DateData[]> {
  return Promise.all(dates.map(fetchDateData))
}
