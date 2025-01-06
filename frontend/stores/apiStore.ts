import axios from 'axios'

export const useApiStore = defineStore('api', () => {
  const runtimeConfig = useRuntimeConfig()
  const baseURL = runtimeConfig.public.serverUrl

  const api = ref(axios.create({
    baseURL,
  }))

  return {
    api,
  }
})
