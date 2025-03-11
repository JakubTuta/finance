<script setup lang="ts">
import type { IFileData } from '~/models/FileData'

const isShow = defineModel('isShow', { type: Boolean, default: false })

const appStore = useAppStore()

const formData = ref<FormData | null>(null)
const wrongFileType = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const fileContents = ref<IFileData[]>([])
const fileLoading = ref(false)

async function save() {
  const financeItems = fileContents.value.map(fileContent => ({
    date: fileContent.date,
    title: fileContent.title,
    amount: fileContent.amount,
    currency: fileContent.currency,
    category: fileContent.category as categories,
    id: '',
    name: fileContent.title, // Using title as name
    isSubscription: false,
    subscription: null,
  }))

  const promises = financeItems.map(financeItem => appStore.addFinanceItem(financeItem))
  await Promise.all(promises)

  close()
}

function close() {
  isShow.value = false
}

function handleFileDrop(event: any) {
  const fileList = event.dataTransfer.files
  handleFile(fileList)
}

function handleFileChoose(event: any) {
  const fileList = event.target.files
  handleFile(fileList)
}

async function handleFile(fileList: any[]) {
  if (fileList.length !== 1)
    return

  const file = fileList[0]
  if (!file.name.endsWith('.csv')) {
    wrongFileType.value = true

    return
  }

  fileLoading.value = true
  wrongFileType.value = false

  formData.value = new FormData()
  formData.value.append('file', file)

  fileContents.value = await appStore.uploadFile(formData.value)
  fileLoading.value = false
}
</script>

<template>
  <v-dialog
    v-model="isShow"
    max-width="1000px"
    scrollable
    @click:outside="close"
  >
    <v-card>
      <v-card-title>
        Read CSV
      </v-card-title>

      <v-divider />

      <v-card-text>
        <div align="center">
          <v-sheet
            class="d-flex align-center justify-center"
            min-height="220px"
            max-width="600px"
            border
            rounded
            :color="wrongFileType
              ? 'rgba(255, 0, 0, 0.05)'
              : formData && formData.get('file')
                ? 'rgba(0, 255, 0, 0.05)'
                : ''"
            @dragover.prevent
            @drop.prevent="handleFileDrop"
          >
            <div class="align-center flex-column flex justify-center">
              <v-icon
                size="48"
                class="mb-2"
              >
                mdi-cloud-upload
              </v-icon>

              <div>
                Drag and drop files here or
              </div>

              <v-btn
                color="primary"
                class="mt-2"
                @click="fileInput?.click()"
              >
                Browse Files
              </v-btn>

              <input
                ref="fileInput"
                type="file"
                style="display: none"
                accept=".csv"
                @change="handleFileChoose"
              >

              <div
                v-if="formData && formData.get('file')"
                class="mt-6"
              >
                {{ (formData.get('file') as File)?.name || '' }}
              </div>
            </div>
          </v-sheet>
        </div>

        <div align="center">
          <v-progress-circular
            v-if="fileLoading"
            indeterminate
            color="primary"
            class="mt-6"
          />
        </div>

        <v-row
          v-if="fileContents.length > 0 && !fileLoading"
          class="ma-1 mt-6"
        >
          <v-col
            v-for="fileContent in fileContents"
            :key="fileContent.date.toISOString()"
            cols="12"
            sm="6"
            class="pa-4"
          >
            <v-card>
              <v-card-title>
                {{ fullDateToString(fileContent.date) }}
              </v-card-title>

              <v-card-text>
                <v-text-field
                  v-model="fileContent.title"
                  label="Title"
                />

                <v-text-field
                  v-model.number="fileContent.amount"
                  label="Amount"
                />

                <v-autocomplete
                  v-model="fileContent.currency"
                  :items="topCurrencies"
                  label="Currency"
                />

                <v-select
                  v-model="fileContent.category as categories"
                  :items="Object.entries(mapCategories).map(([
                    key,
                    value,
                  ]) => ({'title': value,
                          'value': key}))"
                  label="Category"
                />
              </v-card-text>
            </v-card>
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
    </v-card>
  </v-dialog>
</template>
