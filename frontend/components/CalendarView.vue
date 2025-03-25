<script setup lang="ts">
// @ts-expect-error import
import { Qalendar } from 'qalendar'

const selectedDate = ref(new Date())
const useConvertedCurrency = ref(false)
const selectedCurrency = ref<string | null>(null)

const appStore = useAppStore()
const { summaryItems, loading, currencyRates } = storeToRefs(appStore)

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const userStore = useUserStore()

const isPositive = (amount: number) => amount >= 0

const config = {
  defaultMode: 'month',
  disableModes: ['day', 'week'],
  showCurrentTime: false,
  month: {
    showTrailingAndLeadingDates: false,
  },
}

const events = computed(() => {
  console.log(summaryItems.value)
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

  return Object.entries(amountsPerCurrency).map(([currency, amount]) => ({
    rawAmount: amount,
    amount: amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '),
    currency,
    symbol: getCurrencySymbol(currency),
  }))
})

watch(user, (newUser) => {
  if (!newUser)
    return

  selectedCurrency.value = newUser.currency
}, { immediate: true })

watch(selectedDate, async (newDate) => {
  await appStore.getCalendarSummary(newDate)
}, { immediate: true })

function updateCurrency(value: string) {
  if (!value)
    return

  selectedCurrency.value = value
  userStore.updateUser({
    username: user.value?.username || '',
    currency: value,
  })
}

function findEvent(stringDate: string) {
  return events.value.find(event => event.time === stringDate.substring(0, 10))
}

function convertCurrency(amount: number, from: string, to: string) {
  if (!currencyRates.value
    || !currencyRates.value[from]
    // @ts-expect-error correct
    || !currencyRates.value[from][to]) {
    return amount
  }

  // @ts-expect-error correct
  return amount * currencyRates.value[from][to]
}

function getCellColor(time: string) {
  if (!useConvertedCurrency.value || !selectedCurrency.value) {
    return ''
  }

  const event = findEvent(time.substring(0, 10))

  if (!event) {
    return ''
  }

  const convertedAmount = Object.entries(event.amountsPerCurrency).reduce((acc, [currency, amount]) => acc + convertCurrency(amount, currency, selectedCurrency.value!), 0)

  return convertedAmount > 0
    ? 'rgba(0, 255, 0, 0.1)'
    : 'rgba(255, 0, 0, 0.1)'
}

function handleUpdatePeriod(data: { start: Date, end: Date }) {
  const middleDate = new Date((data.start.getTime() + data.end.getTime()) / 2)

  selectedDate.value = middleDate
}

function convertCurrencyForEvent(date: string) {
  if (!useConvertedCurrency.value || !selectedCurrency.value) {
    return
  }

  const event = findEvent(date)

  if (!event) {
    return
  }

  return `${Object.entries(event.amountsPerCurrency).reduce((acc, [currency, amount]) => {
    acc += convertCurrency(amount, currency, selectedCurrency.value!)

    return acc
  }, 0).toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')} ${selectedCurrency.value}`
}
</script>

<template>
  <div style="display: flex; justify-content: center;">
    <v-card
      max-width="1000px"
      color="transparent"
    >
      <v-card-title v-if="monthSummary">
        <v-row class="mt-0">
          <v-checkbox
            v-model="useConvertedCurrency"
            color="primary"
            label="Use converted currency"
          />

          <v-autocomplete
            v-if="useConvertedCurrency"
            v-model="selectedCurrency"
            :items="topCurrencies"
            class="ml-4"
            label="Currency"
            max-width="200"
            @update:model-value="updateCurrency"
          />
        </v-row>

        <div class="mt-3">
          Month total:

          <span
            v-for="amount in monthSummary"
            :key="amount.currency"
            :class="isPositive(amount.rawAmount)
              ? 'text-success'
              : 'text-error'"
            class="mr-2"
          >
            {{ amount.amount }} {{ amount.symbol }}
          </span>
        </div>
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
                v-if="!useConvertedCurrency || !selectedCurrency"
                align="center"
                cols="12"
              >
                <p
                  v-for="([
                    currency,
                    amount,
                  ]) in Object.entries(findEvent(dayData.dateTimeString)?.amountsPerCurrency || {}).slice(0, 2)"
                  :key="currency"
                >
                  {{ `${amount} ${getCurrencySymbol(currency)}` }}
                </p>
              </v-col>

              <v-col
                v-else
                align="center"
                cols="12"
              >
                {{ convertCurrencyForEvent(dayData.dateTimeString) }}
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
