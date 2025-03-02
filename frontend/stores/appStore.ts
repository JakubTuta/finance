export interface FinanceItem {
  id: string | null
  name: string
  amount: number
  category: categories
  date: Date | string
}

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const financeItems = ref<FinanceItem[]>([])
  const summaryItems = ref<{ [key: string]: { [key: string]: number } }>({})

  const apiStore = useApiStore()
  const { api } = storeToRefs(apiStore)

  const mapFinanceItem = (item: any): FinanceItem => {
    return {
      id: item.id,
      name: item.name,
      amount: item.amount,
      category: item.category,
      date: new Date(item.date),
    }
  }

  const fetchFinanceItems = async (startDate: Date, endDate: Date) => {
    loading.value = true

    const url = `/items?startDate=${startDate.toISOString()}&endDate=${endDate.toISOString()}`

    try {
      const response = await api.value.get(url)

      if (response.status === 200) {
        financeItems.value = response.data.map(mapFinanceItem)
      }
    }
    catch (error) {
      console.error(error)
    }

    loading.value = false
  }

  const addFinanceItem = async (
    item: FinanceItem,
    repeatPeriod: string | null = null,
    repeatValue: number | null = null,
  ) => {
    loading.value = true

    const urlParams = new URLSearchParams()

    if (repeatPeriod)
      urlParams.append('repeatPeriod', repeatPeriod)

    if (repeatValue)
      urlParams.append('repeatValue', repeatValue.toString())

    try {
      const url = `/items?${urlParams.toString()}`
      const response = await api.value.post(url, item)

      if (response.status === 201) {
        financeItems.value.push(...response.data.map(mapFinanceItem))
      }
    }
    catch (error) {
      console.error(error)
    }

    loading.value = false
  }

  const updateFinanceItem = async (item: FinanceItem) => {
    loading.value = true

    try {
      const response = await api.value.put(`/items/${item.id}`, item)

      if (response.status === 200) {
        const index = financeItems.value.findIndex(i => i.id === item.id)
        financeItems.value[index] = mapFinanceItem(response.data)
      }
    }
    catch (error) {
      console.error(error)
    }

    loading.value = false
  }

  const deleteFinanceItem = async (item: FinanceItem) => {
    loading.value = true

    const id = item.id

    try {
      const response = await api.value.delete(`/items/${id}`)

      if (response.status === 200) {
        financeItems.value = financeItems.value.filter(i => i.id !== id)
      }
    }
    catch (error) {
      console.error(error)
    }

    loading.value = false
  }

  const getCalendarSummary = async (date: Date) => {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const key = `${year}-${month}`

    if (summaryItems.value[key]) {
      return
    }

    const startDate = startOfMonth(date)
    const endDate = endOfMonth(date)

    const url = `/calendar?startDate=${startDate.toISOString()}&endDate=${endDate.toISOString()}`

    try {
      loading.value = true
      const response = await api.value.get(url)

      if (response.status === 200) {
        summaryItems.value[key] = response.data
      }
    }
    catch (error) {
      console.error(error)
    }
    finally {
      loading.value = false
    }
  }

  return {
    loading,
    financeItems,
    summaryItems,
    fetchFinanceItems,
    addFinanceItem,
    updateFinanceItem,
    deleteFinanceItem,
    getCalendarSummary,
  }
})
