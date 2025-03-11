export interface IFileData {
  title: string
  amount: number
  currency: string
  date: Date
  category: string
}

export function mapFileData(data: any): IFileData {
  return {
    title: data?.title || '',
    amount: data?.amount || 0,
    currency: data?.currency || '',
    date: data?.date
      ? new Date(data.date)
      : new Date(),
    category: data?.category || '',
  }
}
