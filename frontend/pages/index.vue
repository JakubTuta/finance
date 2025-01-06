<script setup lang="ts">
const appStore = useAppStore()

function test() {
  appStore.test()
}
</script>

<template>
  <v-btn @click="test">
    Test
  </v-btn>
</template>
