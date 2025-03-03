import { useUserStore } from '~/stores/user'

export default defineNuxtRouteMiddleware(async (_to, _from) => {
  const accessToken = localStorage.getItem('access')

  if (!accessToken) {
    return navigateTo('/auth/login')
  }

  const userStore = useUserStore()
  const { user } = storeToRefs(userStore)

  if (!user.value) {
    await userStore.getUser()

    if (!user.value) {
      return navigateTo('/auth/login')
    }
  }
})
