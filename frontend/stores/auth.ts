import type { AxiosResponse } from 'axios'
import { jwtDecode } from 'jwt-decode'
import type { IUser } from '~/models/User'
import { mapUser } from '~/models/User'

export const useAuthStore = defineStore('auth', () => {
  const loading = ref(false)
  const initLoading = ref(true)
  const user = ref<IUser | null>(null)

  const apiStore = useApiStore()
  const userStore = useUserStore()
  const router = useRouter()
  const snackbarStore = useSnackbarStore()

  const clearAuth = () => {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    user.value = null
    userStore.resetState()
  }

  const login = async (username: string, password: string) => {
    const url = '/auth/login/'
    const requestData = { username, password }

    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    loading.value = true

    const response = await apiStore.sendRequest({
      url,
      method: 'POST',
      data: requestData,
      headers,
    })

    if (!apiStore.isResponseOk(response)) {
      loading.value = false

      if (response?.status === 400) {
        snackbarStore.showSnackbarError('User with this username doesn\'t exist.')
      }
      else if (response?.status === 401) {
        snackbarStore.showSnackbarError('Invalid password.')
      }
      else {
        snackbarStore.showSnackbarSuccess('Error while logging in.')
      }

      return
    }

    const responseObject = response as AxiosResponse<{ tokens: { access: string, refresh: string }, user: IUser }>
    const responseData = responseObject.data

    const tokens = responseData.tokens

    localStorage.setItem('access', tokens.access)
    localStorage.setItem('refresh', tokens.refresh)

    user.value = mapUser(responseData.user)

    loading.value = false

    router.push('/panel')
  }

  const register = async (username: string, password: string) => {
    const url = '/auth/register/'
    const requestData = { username, password }

    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    loading.value = true

    const response = await apiStore.sendRequest({
      url,
      method: 'POST',
      data: requestData,
      headers,
    })

    if (!apiStore.isResponseOk(response)) {
      loading.value = false

      if (response?.status === 400) {
        snackbarStore.showSnackbarError('User with this username already exists.')
      }
      else {
        snackbarStore.showSnackbarSuccess('Error while registering.')
      }

      return
    }

    const responseObject = response as AxiosResponse<{ tokens: { access: string, refresh: string }, user: IUser }>
    const responseData = responseObject.data

    const tokens = responseData.tokens
    localStorage.setItem('access', tokens.access)
    localStorage.setItem('refresh', tokens.refresh)

    user.value = mapUser(responseData.user)

    loading.value = false

    router.push('/panel')
  }

  const logout = () => {
    clearAuth()
    router.push('/')
  }

  const refreshToken = async () => {
    const refreshToken = localStorage.getItem('refresh')

    if (!refreshToken) {
      return false
    }

    const url = '/auth/token/refresh/'
    const requestData = { refresh: refreshToken }

    const response = await apiStore.sendRequest({
      url,
      method: 'POST',
      data: requestData,
    })

    if (!apiStore.isResponseOk(response)) {
      clearAuth()
      router.push('/')

      return false
    }

    const responseObject = response as AxiosResponse<{ access: string }>
    const accessToken = responseObject.data.access
    localStorage.setItem('access', accessToken)

    return true
  }

  const isTokenValid = async () => {
    const token = localStorage.getItem('access')

    if (!token) {
      return false
    }

    const decodedToken = jwtDecode(token)
    const tokenExp = decodedToken.exp || 0
    const now = Math.floor(Date.now() / 1000)

    if (tokenExp < now) {
      return await refreshToken()
    }
    else {
      return true
    }
  }

  const init = async () => {
    const tokenValid = await isTokenValid()

    if (!tokenValid) {
      clearAuth()
      initLoading.value = false

      return
    }

    const url = '/auth/me/'
    const response = await apiStore.sendRequest({
      url,
      method: 'GET',
    })

    if (!apiStore.isResponseOk(response)) {
      clearAuth()
      initLoading.value = false

      if (!['/auth/login', '/auth/register'].includes(router.currentRoute.value.path)) {
        router.push('/auth/login')
      }

      return
    }

    const responseObject = response as AxiosResponse
    user.value = mapUser(responseObject.data)

    if (['/', '/auth/login', '/auth/register'].includes(router.currentRoute.value.path)) {
      initLoading.value = false
      router.push('/panel')
    }

    initLoading.value = false
  }

  return {
    loading,
    initLoading,
    user,
    login,
    logout,
    register,
    refreshToken,
    isTokenValid,
    init,
  }
})
