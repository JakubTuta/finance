<script setup lang="ts">
import type { IFinanceItem } from '~/models/Finance'

const appStore = useAppStore()
const { financeItems, loading } = storeToRefs(appStore)

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
</script>

<template>
  <v-card :loading="loading">
    <v-card-title>
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
            :class="isPositive(itemsInDate.items.reduce((acc, item) => acc + item.amount, 0))
              ? 'text-success'
              : 'text-error'"
          >
            {{ itemsInDate.items.reduce((acc, item) => acc + item.amount, 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') }} zł
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
              <v-chip :color="mapCategoriesColor[item.category]">
                {{ mapCategories[item.category] }}
              </v-chip>
            </v-card-subtitle>

            <v-card-text
              class="text-subtitle-1"
              style="display: flex; justify-content: space-between; align-items: center;"
            >
              <span>
                {{ `${item.amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')} zł` }}
              </span>

              <v-btn
                size="x-small"
                color="error"
                variant="outlined"
                icon="mdi-window-close"
                @click.stop="appStore.deleteFinanceItem(item)"
              />
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
