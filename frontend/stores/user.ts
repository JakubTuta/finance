import type { AxiosResponse } from 'axios'
import type { IUser } from '~/models/User'
import { mapUser } from '~/models/User'

export const useUserStore = defineStore('user', () => {
  const user = ref<IUser | null>(null)
  const loading = ref(false)

  const apiStore = useApiStore()

  const resetState = () => {
    user.value = null
    loading.value = false
  }

  const getUser = async () => {
    if (user.value)
      return

    loading.value = true

    const token = localStorage.getItem('access')

    if (!token) {
      loading.value = false

      return
    }

    const url = `/auth/me`
    const response = await apiStore.sendRequest({
      url,
      method: 'GET',
    })

    if (!apiStore.isResponseOk(response)) {
      loading.value = false

      return
    }

    const responseObject = response as AxiosResponse
    user.value = mapUser(responseObject.data)

    loading.value = false
  }

  const updateUser = async (data: any) => {
    const url = '/auth/update-user-data/'
    const response = await apiStore.sendRequest({
      url,
      method: 'PUT',
      data,
    })

    if (!apiStore.isResponseOk(response)) {
      return false
    }

    const responseObject = response as AxiosResponse<{ user: IUser }>
    const responseData = responseObject.data

    user.value = mapUser(responseData.user)

    return true
  }

  return {
    user,
    loading,
    resetState,
    getUser,
    updateUser,
  }
})
