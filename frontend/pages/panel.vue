<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const appStore = useAppStore()

onMounted(() => {
  appStore.updateCurrencyRates().then(() => appStore.fetchCurrencyRates())
})

const selectedTab = ref('Detailed')

const tabs = ['Detailed', 'Calendar']
</script>

<template>
  <v-container>
    <v-tabs
      v-model="selectedTab"
      color="primary"
      width="100%"
      class="mb-4"
    >
      <v-tab
        v-for="tab in tabs"
        :key="tab"
        :value="tab"
        grow
      >
        {{ tab }}
      </v-tab>
    </v-tabs>

    <DetailedView v-if="selectedTab === 'Detailed'" />

    <CalendarView v-else />
  </v-container>
</template>
