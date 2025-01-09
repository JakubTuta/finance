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

const categoryItems = Object.entries(mapCategories).map(([key, value]) => ({ title: value, value: key }))

watch(editedItem, (newValue) => {
  if (!newValue)
    return

  name.value = newValue.name
  amount.value = newValue.amount
  date.value = new Date(newValue.date)
  category.value = newValue.category
}, { immediate: true })

function close() {
  isShow.value = false
  name.value = ''
  amount.value = 0
  date.value = new Date()
  category.value = ''
}

function save() {
  if (!name.value || !amount.value || !category.value) {
    valid.value = false

    return
  }

  if (editedItem.value) {
    appStore.updateFinanceItem({
      id: editedItem.value.id,
      name: name.value,
      amount: amount.value,
      date: date.value,
      category: category.value as categories,
    })
  }
  else {
    appStore.addFinanceItem({
      id: '',
      name: name.value,
      amount: amount.value,
      date: date.value,
      category: category.value as categories,
    })
  }

  close()
}

function requiredRule(value: string | number | null, fieldName: string) {
  return !!value || `${fieldName} is required`
}
</script>

<template>
  <v-dialog
    v-model="isShow"
    max-width="600px"
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
            :rules="[() => requiredRule(amount, 'Amount')]"
          />

          <v-text-field
            class="my-4"
            readonly
            label="Date"
            :model-value="dateToString(date)"
          >
            <v-menu activator="parent">
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
            class="mt-4"
            :items="categoryItems"
            label="Category"
            required
            :rules="[() => requiredRule(category, 'Category')]"
          />
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
