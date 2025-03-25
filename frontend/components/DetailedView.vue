<script setup lang="ts">
import type { IFinanceItem } from '~/models/Finance'

const startDate = ref(startOfDay(addDays(new Date(), -30)))
const endDate = ref(endOfDay(new Date()))
const selectedDates = ref<Date[]>(populateSelectedDates())
const selectedMonth = ref(new Date().getMonth())
const selectedYear = ref(new Date().getFullYear())
const isShowDialog = ref(false)
const editedItem = ref<IFinanceItem | null>(null)
const search = ref('')
const selectedCategory = ref<string | null>(null)
const isOpenCSVReadDialog = ref(false)
const isCalendarOpen = ref(false)
const useConvertedCurrency = ref(false)
const selectedCurrency = ref<string | null>(null)

const appStore = useAppStore()
const { financeItems, loading, currencyRates } = storeToRefs(appStore)

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const userStore = useUserStore()

const isPositive = (amount: number) => amount >= 0

const filteredItems = computed(() => {
  const filterByName = (item: IFinanceItem) => {
    if (!search.value)
      return true

    return item.name.toLowerCase().includes(search.value.toLowerCase())
  }

  const filterByCategory = (item: IFinanceItem) => {
    if (!selectedCategory.value)
      return true

    return item.category === selectedCategory.value
  }

  return financeItems.value
    .filter(filterByName)
    .filter(filterByCategory)
})

const itemsPerDate = computed(() => {
  const dates: Date[] = []
  let currentDate = endDate.value

  while (currentDate >= startDate.value) {
    dates.push(currentDate)
    currentDate = addDays(currentDate, -1)
  }

  return dates.map((date) => {
    const items = filteredItems.value.filter(item => isSameDay(new Date(item.date), date))

    return { date, items }
  }).filter(({ items }) => items.length)
})

watch(user, (newUser) => {
  if (!newUser)
    return

  selectedCurrency.value = newUser.currency
}, { immediate: true })

watch(selectedDates, (newValue) => {
  if (!newValue.length)
    return

  startDate.value = startOfDay(newValue[0])
  endDate.value = endOfDay(newValue[newValue.length - 1])
})

watch([startDate, endDate], async ([start, end]) => {
  if (!loading.value && !isCalendarOpen.value)
    await appStore.fetchFinanceItems(start, end)
}, { immediate: true })

watch(isShowDialog, (newValue) => {
  if (!newValue)
    editedItem.value = null
})

watch(isCalendarOpen, (newValue) => {
  if (newValue || !selectedDates.value.length)
    return

  startDate.value = startOfDay(selectedDates.value[0])
  endDate.value = endOfDay(selectedDates.value[selectedDates.value.length - 1])

  appStore.fetchFinanceItems(startDate.value, endDate.value)
})

function populateSelectedDates() {
  const dates: Date[] = []
  let currentDate = startDate.value

  while (currentDate <= endDate.value) {
    dates.push(currentDate)
    currentDate = addDays(currentDate, 1)
  }

  return dates
}

function openDialog(item: IFinanceItem | null) {
  editedItem.value = item
  isShowDialog.value = true
}

function selectLast30Days() {
  startDate.value = startOfDay(addDays(new Date(), -30))
  endDate.value = endOfDay(new Date())

  selectedDates.value = populateSelectedDates()
}

function selectLast7Days() {
  startDate.value = startOfDay(addDays(new Date(), -7))
  endDate.value = endOfDay(new Date())

  selectedDates.value = populateSelectedDates()
}

function selectThisMonth() {
  const selectedDate = new Date(selectedYear.value, selectedMonth.value, 1)
  startDate.value = startOfMonth(selectedDate)
  endDate.value = endOfMonth(selectedDate)

  selectedDates.value = populateSelectedDates()
}

function onMonthChange(newMonth: number) {
  selectedMonth.value = newMonth
}

function onYearChange(newYear: number) {
  selectedYear.value = newYear
}

function openCSVReadDialog() {
  isOpenCSVReadDialog.value = true
}

function getNextSubscriptionPayment(item: IFinanceItem) {
  if (!item.isSubscription || !item.subscription)
    return ''

  const nextDate = new Date(item.date)

  switch (item.subscription.repeatPeriod) {
    case 'day':
      nextDate.setDate(nextDate.getDate() + item.subscription.repeatValue)
      break
    case 'week':
      nextDate.setDate(nextDate.getDate() + item.subscription.repeatValue * 7)
      break
    case 'month':
      nextDate.setMonth(nextDate.getMonth() + item.subscription.repeatValue)
      break
    default:
      return ''
  }

  if (item.subscription.endDate && nextDate > new Date(item.subscription.endDate))
    return 'Ended'

  return dateToString(nextDate)
}

function updateCurrency(value: string) {
  if (!value)
    return

  selectedCurrency.value = value
  userStore.updateUser({
    username: user.value?.username || '',
    currency: value,
  })
}

function calculateItemAmount(item: IFinanceItem): number {
  if (useConvertedCurrency.value
    && selectedCurrency.value
    && item.currency !== selectedCurrency.value
    && currencyRates.value
    && currencyRates.value[item.currency]
    // @ts-expect-error correct
    && currencyRates.value[item.currency][selectedCurrency.value]) {
    // @ts-expect-error correct
    const rate = currencyRates.value[item.currency][selectedCurrency.value]

    return item.amount * rate
  }

  return item.amount
}

function getItemAmount(item: IFinanceItem): string {
  const amount = calculateItemAmount(item)
  const currency = useConvertedCurrency.value && selectedCurrency.value
    ? selectedCurrency.value
    : item.currency

  return `${amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')} ${getCurrencySymbol(currency)}`
}

function dailyAmount(date: Date) {
  if (useConvertedCurrency.value && selectedCurrency.value) {
    return financeItems.value
      .filter(item => isSameDay(new Date(item.date), date))
      .reduce((acc, item) => acc + calculateItemAmount(item), 0)
  }

  // When not using converted currency, we return null as we'll use the groupedByCurrency in the string function
  return null
}

function dailyAmountToString(date: Date) {
  if (useConvertedCurrency.value && selectedCurrency.value) {
    const amount = dailyAmount(date) as number

    return [{
      rawAmount: amount,
      amount: amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '),
      currency: selectedCurrency.value,
      symbol: getCurrencySymbol(selectedCurrency.value),
    }]
  }
  else {
    const items = financeItems.value.filter(item => isSameDay(new Date(item.date), date))
    const groupedByCurrency = items.reduce((acc, item) => {
      if (!acc[item.currency]) {
        acc[item.currency] = 0
      }
      acc[item.currency] += item.amount

      return acc
    }, {} as Record<string, number>)

    return Object.entries(groupedByCurrency).map(([currency, amount]) => ({
      rawAmount: amount,
      amount: amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '),
      currency,
      symbol: getCurrencySymbol(currency),
    }))
  }
}
</script>

<template>
  <v-card :loading="loading">
    <v-card-title>
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

      <v-row
        class="pa-2"
        style="display: flex; justify-content: space-between; align-items: center;"
      >
        <div class="text-primary text-h6 cursor-pointer">
          {{ dateToString(startDate) === dateToString(endDate)
            ? `Date: ${dateToString(startDate)}`
            : `Dates: ${dateToString(startDate)} - ${dateToString(endDate)}` }}

          <v-menu
            v-model="isCalendarOpen"
            activator="parent"
            :close-on-content-click="false"
          >
            <v-card max-width="350">
              <v-card-text>
                <v-date-picker
                  v-model="selectedDates"
                  :year="new Date().getFullYear()"
                  :month="new Date().getMonth()"
                  :first-day-of-week="1"
                  color="primary"
                  width="100%"
                  multiple="range"
                  landscape
                  show-adjacent-months
                  hide-header
                  @update:month="onMonthChange"
                  @update:year="onYearChange"
                />
              </v-card-text>

              <v-card-actions>
                <v-btn
                  size="small"
                  @click="selectLast30Days"
                >
                  Last 30 days
                </v-btn>

                <v-btn
                  size="small"
                  @click="selectLast7Days"
                >
                  Last 7 days
                </v-btn>

                <v-btn
                  size="small"
                  @click="selectThisMonth"
                >
                  This month
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-menu>
        </div>

        <div class="mt-1">
          <v-btn
            prepend-icon="mdi-file-delimited-outline"
            color="primary"
            @click="openCSVReadDialog"
          >
            Import from CSV
          </v-btn>

          <v-btn
            class="ml-4"
            prepend-icon="mdi-plus"
            color="primary"
            @click="openDialog(null)"
          >
            Add new
          </v-btn>
        </div>
      </v-row>

      <v-row>
        <v-col cols="4">
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            label="Search"
            clearable
          />
        </v-col>

        <v-col cols="4">
          <v-select
            v-model="selectedCategory"
            :items="Object.entries(mapCategories).map(([
              key,
              value,
            ]) => ({'title': value,
                    'value': key}))"
            label="Filter by category"
            clearable
          />
        </v-col>
      </v-row>
    </v-card-title>

    <v-card-text class="mt-4">
      <v-row
        v-for="(itemsInDate, index) in itemsPerDate"
        :key="dateToString(itemsInDate.date)"
        :class="index === 0
          ? 'mx-1'
          : 'mx-1 mt-6'"
      >
        <span class="text-h6">
          {{ dateToString(itemsInDate.date) }}
        </span>

        <span class="text-h6 ml-6">
          Daily:

          <span
            v-for="amount in dailyAmountToString(itemsInDate.date)"
            :key="amount.currency"
            :class="isPositive(amount.rawAmount)
              ? 'text-success'
              : 'text-error'"
            class="mr-2"
          >
            {{ amount.amount }} {{ amount.symbol }}
          </span>
        </span>

        <v-divider class="mb-1 mt-2" />

        <v-col
          v-for="item in itemsInDate.items"
          :key="item.id || ''"
          cols="12"
          sm="4"
          md="3"
          lg="2"
        >
          <v-card
            flat
            variant="outlined"
            :color="isPositive(item.amount)
              ? 'success'
              : 'error'"
            @click="() => openDialog(item)"
          >
            <v-card-title>
              {{ item.name }}
            </v-card-title>

            <v-card-subtitle>
              <div class="justify-space-between align-center flex">
                <v-chip :color="mapCategoriesColor[item.category]">
                  {{ mapCategories[item.category] }}
                </v-chip>

                <v-tooltip location="bottom">
                  <template #activator="{props}">
                    <v-icon
                      v-if="item.isSubscription"
                      color="warning"
                      v-bind="props"
                    >
                      mdi-reload
                    </v-icon>
                  </template>

                  <p>
                    Subscription
                  </p>

                  <p>
                    Next payment: {{ getNextSubscriptionPayment(item) }}
                  </p>
                </v-tooltip>
              </div>
            </v-card-subtitle>

            <v-card-text
              class="text-subtitle-1"
              style="display: flex; justify-content: space-between; align-items: center;"
            >
              <span>
                {{ getItemAmount(item) }}
              </span>

              <div>
                <v-tooltip location="bottom">
                  <template #activator="{props}">
                    <v-btn
                      v-if="item.isSubscription"
                      v-bind="props"
                      class="mx-1"
                      size="x-small"
                      color="warning"
                      variant="outlined"
                      icon="mdi-pause"
                      @click.stop="appStore.pauseSubscription(item, itemsInDate.date)"
                    />
                  </template>

                  Pause this subscription
                </v-tooltip>

                <v-btn
                  size="x-small"
                  color="error"
                  variant="outlined"
                  icon="mdi-window-close"
                  @click.stop="appStore.deleteFinanceItem(item)"
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>

  <FinanceDialog
    v-model:is-show="isShowDialog"
    :edited-item="editedItem"
  />

  <ReadCSVDialog
    v-model:is-show="isOpenCSVReadDialog"
  />
</template>
