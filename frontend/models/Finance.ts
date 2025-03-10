export interface IFinanceItem {
  id: string | null
  name: string
  amount: number
  category: categories
  date: Date | string
  currency: string
  // subscription
  isSubscription: boolean
  subscription: {
    startDate: Date
    endDate: Date | null
    repeatPeriod: 'day' | 'week' | 'month'
    repeatValue: number
  } | null
}

export function mapFinanceItem(item: any): IFinanceItem {
  return {
    id: item.id || null,
    name: item.name || '',
    amount: item.amount || 0,
    category: item.category || 'others',
    date: item.date
      ? new Date(item.date)
      : new Date(),
    currency: item.currency || 'USD',
    isSubscription: item.is_subscription || false,
    subscription: item.is_subscription && item.start_date && item.repeat_period && item.repeat_value
      ? {
          startDate: new Date(item.start_date),
          endDate: item.end_date
            ? new Date(item.end_date)
            : null,
          repeatPeriod: item.repeat_period,
          repeatValue: item.repeat_value,
        }
      : null,
  }
}
