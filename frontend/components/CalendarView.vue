<script setup lang="ts">
// @ts-expect-error import
import { Qalendar } from 'qalendar'

const appStore = useAppStore()
const { summaryItems, loading } = storeToRefs(appStore)

const selectedDate = ref(new Date())

const config = {
  defaultMode: 'month',
  disableModes: ['day', 'week'],
  showCurrentTime: false,
  month: {
    showTrailingAndLeadingDates: false,
  },
}

const events = computed(() => {
  const year = selectedDate.value.getFullYear()
  const month = (selectedDate.value.getMonth() + 1).toString().padStart(2, '0')
  const key = `${year}-${month}`

  if (!summaryItems.value[key]) {
    return []
  }

  return Object.entries(summaryItems.value[key]).map(([date, amount]) => {
    return {
      title: amount,
      time: date,
    }
  })
})

watch(selectedDate, async (newDate) => {
  await appStore.getCalendarSummary(newDate)
}, { immediate: true })

function findEvent(stringDate: string) {
  return events.value.find(event => event.time === stringDate)
}

function getCellColor(time: string) {
  const event = findEvent(time.substring(0, 10))

  if (!event) {
    return ''
  }

  return event.title > 0
    ? 'rgba(0, 255, 0, 0.1)'
    : 'rgba(255, 0, 0, 0.1)'
}

function handleUpdatePeriod(data: { start: Date, end: Date }) {
  const middleDate = new Date((data.start.getTime() + data.end.getTime()) / 2)

  selectedDate.value = middleDate
}
</script>

<template>
  <div style="display: flex; justify-content: center;">
    <v-card
      max-width="1000px"
      color="transparent"
    >
      <v-card-title>
        Month total: {{ events.reduce((acc, event) => acc + event.title, 0).toFixed(2) }} zł
      </v-card-title>

      <v-card-text>
        <Qalendar
          :selected-date="selectedDate"
          :config="config"
          :is-loading="loading"
          @updated-period="handleUpdatePeriod"
        >
          <template #dayCell="{dayData}">
            <v-row
              style="min-height: 110px; width: 100%;"
              :style="`background-color: ${getCellColor(dayData.dateTimeString)}`"
            >
              <v-col
                cols="12"
                align="center"
              >
                {{ dayData.dateTimeString.substring(8, 10) }}
              </v-col>

              <v-col
                cols="12"
                align="center"
              >
                {{ findEvent(dayData.dateTimeString.substring(0, 10))?.title }}
              </v-col>
            </v-row>
          </template>
        </Qalendar>
      </v-card-text>
    </v-card>
  </div>
</template>

<style>
  @import "qalendar/dist/style.css";
</style>
