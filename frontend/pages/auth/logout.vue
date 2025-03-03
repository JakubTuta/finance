<script setup lang="ts">
const authStore = useAuthStore()

onMounted(() => {
  authStore.logout()
})
</script>

<template>
  Logging out...
</template>
