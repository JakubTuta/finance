import type { AxiosResponse } from 'axios'
import axios, { AxiosError } from 'axios'

export const useApiStore = defineStore('api', () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.SERVER_URL as string

  const defaultHeaders = {
    'Content-Type': 'application/json',
  }

  const api = axios.create({
    baseURL,
    responseType: 'json',
    headers: defaultHeaders,
  })

  api.interceptors.request.use((config) => {
    const accessToken = localStorage.getItem('access')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    return config
  }, (error) => {
    return Promise.reject(error)
  })

  const sendRequest = async (
    { url, method, data, headers = null }:
    { url: string, method: 'GET' | 'POST' | 'PUT' | 'DELETE', data?: any, headers?: any },
  ): Promise<AxiosResponse | AxiosError | null> => {
    let response: AxiosResponse | null = null

    const requestHeaders = headers || defaultHeaders

    try {
      switch (method) {
        case 'GET':
          response = await api.get(url, { headers: requestHeaders })
          break
        case 'POST':
          response = await api.post(url, data, { headers: requestHeaders })
          break
        case 'PUT':
          response = await api.put(url, data, { headers: requestHeaders })
          break
        case 'DELETE':
          response = await api.delete(url, { headers: requestHeaders })
          break
        default:
          break
      }
    }
    catch (error) {
      console.error(error)

      return error as AxiosError
    }

    return response
  }

  const isResponseOk = (response: AxiosResponse | AxiosError | null): boolean => {
    return response !== null && !(response instanceof AxiosError) && response.status >= 200 && response.status < 300
  }

  return {
    sendRequest,
    isResponseOk,
  }
})
