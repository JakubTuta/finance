import type { AxiosResponse } from 'axios'
import type { ICalendarDay } from '~/models/CalendarDay'
import { mapFileData } from '~/models/FileData'
import type { IFinanceItem } from '~/models/Finance'
import { mapFinanceItem } from '~/models/Finance'

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const financeItems = ref<IFinanceItem[]>([])
  const summaryItems = ref<{ [key: string]: ICalendarDay }>({})

  const apiStore = useApiStore()

  const fetchFinanceItems = async (startDate: Date, endDate: Date) => {
    loading.value = true

    const url = `/finances/?startDate=${startDate.toISOString()}&endDate=${endDate.toISOString()}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const responseObject = response as AxiosResponse
      financeItems.value = responseObject.data.map(mapFinanceItem)
    }

    loading.value = false
  }

  const addFinanceItem = async (
    item: IFinanceItem,
    repeatPeriod: string | null = null,
    repeatValue: number | null = null,
  ) => {
    loading.value = true

    const urlParams = new URLSearchParams()

    if (repeatPeriod)
      urlParams.append('repeatPeriod', repeatPeriod)

    if (repeatValue)
      urlParams.append('repeatValue', repeatValue.toString())

    const url = `/finances/?${urlParams.toString()}`
    const response = await apiStore.sendRequest({ url, method: 'POST', data: item })

    if (apiStore.isResponseOk(response)) {
      const responseObject = response as AxiosResponse
      financeItems.value.push(...responseObject.data.map(mapFinanceItem))
    }

    loading.value = false
  }

  const updateFinanceItem = async (item: IFinanceItem) => {
    loading.value = true

    const url = `/finances/${item.id}/`
    const response = await apiStore.sendRequest({ url, method: 'PUT', data: item })

    if (apiStore.isResponseOk(response)) {
      const responseObject = response as AxiosResponse
      const index = financeItems.value.findIndex((i: IFinanceItem) => i.id === item.id)
      financeItems.value[index] = mapFinanceItem(responseObject.data)
    }

    loading.value = false
  }

  const deleteFinanceItem = async (item: IFinanceItem) => {
    loading.value = true

    const id = item.id

    const url = `/finances/${id}/`
    const response = await apiStore.sendRequest({ url, method: 'DELETE' })

    if (apiStore.isResponseOk(response)) {
      financeItems.value = financeItems.value.filter((i: IFinanceItem) => i.id !== id)
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

    loading.value = true

    const startDate = startOfMonth(date)
    const endDate = endOfMonth(date)

    const url = `/calendar/?startDate=${startDate.toISOString()}&endDate=${endDate.toISOString()}`

    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const responseObject = response as AxiosResponse
      summaryItems.value[key] = responseObject.data
    }

    loading.value = false
  }

  const pauseSubscription = async (item: IFinanceItem, date: Date) => {
    loading.value = true

    const url = `/finances/${item.id}/pause/?endDate=${date.toISOString()}`
    const response = await apiStore.sendRequest({ url, method: 'GET' })

    if (apiStore.isResponseOk(response)) {
      const responseObject = response as AxiosResponse
      financeItems.value = financeItems.value.filter((item) => {
        if (item.id !== responseObject.data.id) {
          return true
        }

        return item.date < date
      })
    }

    loading.value = false
  }

  const uploadFile = async (formData: FormData | null) => {
    if (!formData) {
      return
    }

    const url = '/finances/upload/'

    const response = await apiStore.sendRequest({ url, method: 'POST', data: formData, headers: { 'Content-Type': 'multipart/form-data' } })

    if (apiStore.isResponseOk(response)) {
      const responseObject = response as AxiosResponse

      return responseObject.data.map(mapFileData)
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
    pauseSubscription,
    uploadFile,
  }
})
