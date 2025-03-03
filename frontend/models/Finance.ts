export interface IFinanceItem {
  id: string | null
  name: string
  amount: number
  category: categories
  date: Date | string
}

export function mapFinanceItem(item: Partial<IFinanceItem>): FinanceItem {
  return {
    id: item.id || null,
    name: item.name || '',
    amount: item.amount || 0,
    category: item.category || 'others',
    date: item.date
      ? new Date(item.date)
      : new Date(),
  }
}
