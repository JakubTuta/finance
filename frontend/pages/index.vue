<script setup lang="ts">
const appStore = useAppStore()
const { financeItems } = storeToRefs(appStore)

const startDate = ref(startOfDay(addDays(new Date(), -30)))
const endDate = ref(endOfDay(new Date()))
const selectedDates = ref<Date[]>(populateSelectedDates())
const isShowDialog = ref(false)
const editedItem = ref<FinanceItem | null>(null)
const search = ref('')
const selectedCategory = ref<string | null>(null)

const isPositive = (amount: number) => amount >= 0

const filteredItems = computed(() => {
  const filterByName = (item: FinanceItem) => {
    if (!search.value)
      return true

    return item.name.toLowerCase().includes(search.value.toLowerCase())
  }

  const filterByCategory = (item: FinanceItem) => {
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
    const items = filteredItems.value.filter((item: FinanceItem) => isSameDay(new Date(item.date), date))

    return { date, items }
  }).filter(({ items }) => items.length)
})

watch(selectedDates, (newValue) => {
  if (!newValue.length)
    return

  startDate.value = startOfDay(newValue[0])
  endDate.value = endOfDay(newValue[newValue.length - 1])
})

watch([startDate, endDate], ([start, end]) => {
  appStore.fetchFinanceItems(start, end)
}, { immediate: true })

watch(isShowDialog, (newValue) => {
  if (!newValue)
    editedItem.value = null
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

function openDialog(item: FinanceItem | null) {
  editedItem.value = item
  isShowDialog.value = true
}
</script>

<template>
  <v-container>
    <v-card>
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
              activator="parent"
              :close-on-content-click="false"
            >
              <v-card max-width="350">
                <v-card-text>
                  <v-date-picker
                    v-model="selectedDates"
                    :year="new Date().getFullYear()"
                    :month="new Date().getMonth()"
                    color="primary"
                    :first-day-of-week="1"
                    width="100%"
                    hide-header
                    landscape
                    multiple="range"
                  />
                </v-card-text>
              </v-card>
            </v-menu>
          </div>

          <v-btn
            prepend-icon="mdi-plus"
            color="primary"
            @click="openDialog(null)"
          >
            Add new
          </v-btn>
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
            :key="item.id"
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
  </v-container>

  <FinanceDialog
    v-model:is-show="isShowDialog"
    :edited-item="editedItem"
  />
</template>
