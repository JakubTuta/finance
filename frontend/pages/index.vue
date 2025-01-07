<script setup lang="ts">
const appStore = useAppStore()
const { financeItems } = storeToRefs(appStore)

const startDate = ref(startOfDay(addDays(new Date(), -30)))
const endDate = ref(endOfDay(new Date()))
const selectedDates = ref<Date[]>(populateSelectedDates())
const isShowDialog = ref(false)
const editedItem = ref<FinanceItem | null>(null)

const isPositive = (amount: number) => amount >= 0

const mapCategories: { [key: string]: string } = {
  entertainment: 'Entertainment',
  food: 'Food',
  groceries: 'Groceries',
  others: 'Others',
}

const itemsPerDate = computed(() => {
  const dates: Date[] = []
  let currentDate = startDate.value

  while (currentDate <= endDate.value) {
    dates.push(currentDate)
    currentDate = addDays(currentDate, 1)
  }

  return dates.map((date) => {
    const items = financeItems.value.filter(item => isSameDay(new Date(item.date), date))

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
      <v-card-title style="display: flex; justify-content: space-between; align-items: center;">
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
      </v-card-title>

      <v-card-text class="mt-2">
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
                {{ mapCategories[item.category] }}
              </v-card-subtitle>

              <v-card-text
                class="text-subtitle-1"
                style="display: flex; justify-content: space-between; align-items: center;"
              >
                <span>
                  {{ `${item.amount} zł` }}
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
