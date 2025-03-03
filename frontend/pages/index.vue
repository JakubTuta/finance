<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const router = useRouter()

const authStore = useAuthStore()
const { user, initLoading } = storeToRefs(authStore)

watch(initLoading, (newLoading) => {
  if (!newLoading && user.value)
    router.push('/panel')
}, { immediate: true })
</script>

<template>
  <v-container style="display: flex; align-items: center; justify-content: center; height: 100%">
    <div
      class="text-h5"
    >
      <span class="text-h4">
        Welcome to Finance!
      </span>

      <p class="my-2">
        A smart money management app that helps you track your spending and income. Powered by AI to identify savings opportunities and improve your financial health.
      </p>

      <p>
        To get started,

        <NuxtLink to="/auth/login">
          <v-btn
            variant="text"
            color="primary"
            class="mx-2"
          >
            Login
          </v-btn>
        </NuxtLink>

        or

        <NuxtLink to="/auth/register">
          <v-btn
            variant="text"
            color="primary"
            class="mx-2"
          >
            Register
          </v-btn>
        </NuxtLink>
      </p>
    </div>
  </v-container>
</template>
