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

  return Object.entries(summaryItems.value[key]).map(([date, amountsPerCurrency]) => {
    return {
      time: date,
      amountsPerCurrency,
    }
  })
})

const monthSummary = computed(() => {
  const amountsPerCurrency = events.value.reduce((acc, event) => {
    return Object.entries(event.amountsPerCurrency).reduce((acc, [currency, amount]) => {
      if (!acc[currency]) {
        acc[currency] = 0
      }

      acc[currency] += amount

      return acc
    }, acc)
  }, {} as Record<string, number>)

  return Object.entries(amountsPerCurrency).map(([currency, amount]) => `${amount} ${getCurrencySymbol(currency)}`).join(', ')
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

  return 'rgba(255, 255, 255, 0.15)'

  // return event.title > 0
  //   ? 'rgba(0, 255, 0, 0.1)'
  //   : 'rgba(255, 0, 0, 0.1)'
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
      <v-card-title v-if="monthSummary">
        Month total: {{ monthSummary }}
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
              style="min-height: 120px; width: 100%;"
              :style="`background-color: ${getCellColor(dayData.dateTimeString)}`"
            >
              <v-tooltip
                v-if="events.find(e => e.time === dayData.dateTimeString.substring(0, 10))?.amountsPerCurrency"
                activator="parent"
              >
                <p
                  v-for="([
                    currency,
                    amount,
                  ]) in Object.entries(events.find(e => e.time === dayData.dateTimeString.substring(0, 10))?.amountsPerCurrency || {}).slice(0, 2)"
                  :key="currency"
                >
                  {{ `${amount} ${getCurrencySymbol(currency)}` }}
                </p>
              </v-tooltip>

              <v-col
                cols="12"
                align="center"
              >
                {{ dayData.dateTimeString.substring(8, 10) }}
              </v-col>

              <v-col
                align="center"
                cols="12"
              >
                <p
                  v-for="([
                    currency,
                    amount,
                  ]) in Object.entries(events.find(e => e.time === dayData.dateTimeString.substring(0, 10))?.amountsPerCurrency || {}).slice(0, 2)"
                  :key="currency"
                >
                  {{ `${amount} ${getCurrencySymbol(currency)}` }}
                </p>
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
