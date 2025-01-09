export interface FinanceItem {
  id: string
  name: string
  amount: number
  category: categories
  date: Date | string
}

export const useAppStore = defineStore('app', () => {
  const apiStore = useApiStore()
  const { api } = storeToRefs(apiStore)

  const financeItems = ref<FinanceItem[]>([])

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
  }

  const addFinanceItem = async (item: FinanceItem) => {
    try {
      const response = await api.value.post('/items', item)

      if (response.status === 201) {
        financeItems.value.push(mapFinanceItem(response.data))
      }
    }
    catch (error) {
      console.error(error)
    }
  }

  const updateFinanceItem = async (item: FinanceItem) => {
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
  }

  const deleteFinanceItem = async (item: FinanceItem) => {
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
  }

  return {
    financeItems,
    fetchFinanceItems,
    addFinanceItem,
    updateFinanceItem,
    deleteFinanceItem,
  }
})
