<script setup lang="ts">
const props = defineProps<{
  editedItem: FinanceItem | null
}>()

const { editedItem } = toRefs(props)

const isShow = defineModel('isShow', { type: Boolean, default: false })

const appStore = useAppStore()

const name = ref('')
const amount = ref(0)
const date = ref(new Date())
const category = ref('')

const categoryItems = [
  {
    title: 'Entertainment',
    value: 'entertainment',
  },
  {
    title: 'Food',
    value: 'food',
  },
  {
    title: 'Groceries',
    value: 'groceries',
  },
  {
    title: 'Others',
    value: 'others',
  },
]

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
  if (!name.value || !amount.value || !category.value)
    return

  if (editedItem.value) {
    appStore.updateFinanceItem({
      id: editedItem.value.id,
      name: name.value,
      amount: amount.value,
      date: date.value,
      category: category.value,
    })
  }
  else {
    appStore.addFinanceItem({
      id: '',
      name: name.value,
      amount: amount.value,
      date: date.value,
      category: category.value,
    })
  }

  close()
}
</script>

<template>
  <v-dialog
    v-model="isShow"
    max-width="600px"
    @click:outside="close"
  >
    <v-card>
      <v-card-title>
        {{ editedItem
          ? 'Edit'
          : 'Add' }} Finance Item
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-form>
          <v-text-field
            v-model="name"
            class="mb-2"
            label="Name"
            required
          />

          <v-text-field
            v-model="amount"
            class="my-2"
            label="Amount"
            required
          />

          <v-text-field
            class="my-2"
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
            class="mt-2"
            :items="categoryItems"
            label="Category"
            required
          />
        </v-form>
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
          @click="save"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
