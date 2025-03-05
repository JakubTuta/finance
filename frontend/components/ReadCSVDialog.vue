<script setup lang="ts">
const isShow = defineModel('isShow', { type: Boolean, default: false })

const appStore = useAppStore()

const formData = ref<FormData | null>(null)
const wrongFileType = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function save() {
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

function handleFile(fileList: any[]) {
  if (fileList.length !== 1)
    return

  const file = fileList[0]
  if (!file.name.endsWith('.csv')) {
    wrongFileType.value = true

    return
  }

  wrongFileType.value = false

  formData.value = new FormData()
  formData.value.append('file', file)

  appStore.uploadFile(formData.value)
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
