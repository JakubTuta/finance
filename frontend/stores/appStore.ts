export const useAppStore = defineStore('app', () => {
  const apiStore = useApiStore()
  const { api } = storeToRefs(apiStore)

  const test = async () => {
    const url = '/'

    try {
      const response = await api.value.get(url)

      console.log(response)
    }
    catch (error) {
      console.error(error)
    }
  }

  return {
    test,
  }
})
