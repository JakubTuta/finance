<script setup lang="ts">
const props = defineProps<{
  editedItem: FinanceItem | null
}>()

const { editedItem } = toRefs(props)

const isShow = defineModel('isShow', { type: Boolean, default: false })

const appStore = useAppStore()

const name = ref('')
const amount = ref<number | null>(null)
const date = ref(new Date())
const category = ref<string | null>(null)
const valid = ref(false)
const paymentType = ref('one-time')
const recurringPaymentCount = ref(1)
const recurringPaymentInterval = ref('day')

const categoryItems = Object.entries(mapCategories).map(([key, value]) => ({ title: value, value: key }))

watch(editedItem, (newValue) => {
  if (!newValue)
    return

  name.value = newValue.name
  amount.value = newValue.amount
  date.value = new Date(newValue.date)
  category.value = newValue.category
  paymentType.value = newValue.next_payment
    ? 'recurring'
    : 'one-time'
  recurringPaymentCount.value = newValue.next_payment_interval_value || 1
  recurringPaymentInterval.value = newValue.next_payment_interval || 'day'
}, { immediate: true })

function close() {
  isShow.value = false
  name.value = ''
  amount.value = 0
  date.value = new Date()
  category.value = ''
  valid.value = false
  paymentType.value = 'one-time'
  recurringPaymentCount.value = 1
  recurringPaymentInterval.value = 'day'
}

function save() {
  if (!name.value || !amount.value || !category.value) {
    valid.value = false

    return
  }

  let nextPayment = null

  if (paymentType.value === 'recurring') {
    nextPayment = new Date(date.value)

    switch (recurringPaymentInterval.value) {
      case 'day':
        nextPayment.setDate(nextPayment.getDate() + recurringPaymentCount.value)
        break
      case 'week':
        nextPayment.setDate(nextPayment.getDate() + recurringPaymentCount.value * 7)
        break
      case 'month':
        nextPayment.setMonth(nextPayment.getMonth() + recurringPaymentCount.value)
        break
    }
  }

  const financeObject: FinanceItem = {
    id: editedItem.value?.id || null,
    name: name.value,
    amount: amount.value,
    date: date.value,
    category: category.value as categories,
    next_payment: nextPayment,
    next_payment_interval: paymentType.value === 'recurring'
      ? recurringPaymentInterval.value
      : null,
    next_payment_interval_value: paymentType.value === 'recurring'
      ? recurringPaymentCount.value
      : null,
  }

  if (editedItem.value) {
    appStore.updateFinanceItem(financeObject)
  }
  else {
    appStore.addFinanceItem(financeObject)
  }

  close()
}

function requiredRule(value: string | number | null, fieldName: string) {
  return !!value || `${fieldName} is required`
}

function numberRule(value: any, fieldName: string) {
  return /^-?(?:\d+(?:\.\d+)?|\.\d+)$/.test(value) || `${fieldName} must be a valid number`
}

function positiveIntRule(value: number, fieldName: string) {
  return Number.isInteger(value) && value > 0 || `${fieldName} must be a positive integer`
}
</script>

<template>
  <v-dialog
    v-model="isShow"
    max-width="600px"
    scrollable
    @click:outside="close"
  >
    <v-card>
      <v-form
        v-model="valid"
        @submit.prevent
      >
        <v-card-title>
          {{ editedItem
            ? 'Edit'
            : 'Add' }} Finance Item
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-text-field
            v-model="name"
            class="mb-4"
            label="Name"
            required
            :rules="[() => requiredRule(name, 'Name')]"
          />

          <v-text-field
            v-model.number="amount"
            class="my-4"
            label="Amount"
            required
            :rules="[
              () => requiredRule(amount, 'Amount'),
              numberRule(amount, 'Amount'),
            ]"
          />

          <v-text-field
            class="my-4"
            readonly
            label="Date"
            :model-value="dateToString(date)"
          >
            <v-menu
              activator="parent"
              :close-on-content-click="false"
            >
              <v-card max-width="350">
                <v-card-text>
                  <v-date-picker
                    v-model="date"
                    :year="new Date().getFullYear()"
                    :month="new Date().getMonth()"
                    color="primary"
                    :first-day-of-week="1"
                    width="100%"
                    hide-header
                    landscape
                  />
                </v-card-text>
              </v-card>
            </v-menu>
          </v-text-field>

          <v-select
            v-model="category"
            class="my-4"
            :items="categoryItems"
            label="Category"
            required
            :rules="[() => requiredRule(category, 'Category')]"
          />

          <span>
            Payment Type
          </span>

          <v-btn-toggle
            v-model="paymentType"
            width="100%"
            class="my-4"
            color="primary"
            variant="outlined"
            density="comfortable"
            style="width: 100%"
          >
            <v-btn
              value="one-time"
              width="50%"
            >
              One-time
            </v-btn>

            <v-btn
              value="recurring"
              width="50%"
            >
              Recurring
            </v-btn>
          </v-btn-toggle>

          <v-row
            v-if="paymentType === 'recurring'"
            class="mt-4"
          >
            <v-col
              cols="12"
              sm="6"
            >
              <v-text-field
                v-model.number="recurringPaymentCount"
                label="Count"
                :rules="paymentType === 'one-time'
                  ? []
                  : [
                    () => requiredRule(recurringPaymentCount, 'Count'),
                    positiveIntRule(recurringPaymentCount, 'Count'),
                  ]"
              />
            </v-col>

            <v-col
              cols="12"
              sm="6"
            >
              <v-select
                v-model="recurringPaymentInterval"
                :items="[
                  'day',
                  'week',
                  'month',
                ]"
                label="Interval"
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-spacer />

          <v-btn
            color="error"
            variant="text"
            @click="close"
          >
            Cancel
          </v-btn>

          <v-btn
            color="success"
            variant="text"
            type="submit"
            @click="save"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>
