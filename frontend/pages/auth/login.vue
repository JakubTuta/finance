<script setup lang="ts">
const router = useRouter()

const authStore = useAuthStore()
const { loading } = storeToRefs(authStore)

const { form, valid, isValid } = useForm()

const username = ref('')
const password = ref('')
const isShowPassword = ref(false)

function goBack() {
  router.push('/')
}

async function login() {
  if (await isValid())
    authStore.login(username.value, password.value)
}
</script>

<template>
  <div style="display: flex; align-items: center; justify-content: center; height: 100%">
    <v-btn
      style="position: absolute; top: 20px; left: 20px;"
      prepend-icon="mdi-arrow-left"
      @click="goBack"
    >
      Back
    </v-btn>

    <v-card max-width="600px">
      <v-card-title class="text-h4">
        Login
      </v-card-title>

      <v-divider class="my-2" />

      <v-card-text>
        <v-form
          ref="form"
          v-model="valid"
          @submit.prevent="login"
        >
          <v-text-field
            v-model="username"
            class="mb-4"
            label="Username"
            :rules="[
              requiredRule('Username'),
              minLengthRule(3),
              maxLengthRule(20),
            ]"
            @keydown.enter="login"
          />

          <v-text-field
            v-model="password"
            label="Password"
            variant="outlined"
            :type="isShowPassword
              ? 'text'
              : 'password'"
            :append-inner-icon="isShowPassword
              ? 'mdi-eye'
              : 'mdi-eye-off'"
            :rules="[
              requiredRule('Password'),
              minLengthRule(6),
              maxLengthRule(20),
            ]"
            @click:append-inner="isShowPassword = !isShowPassword"
            @keydown.enter="login"
          />
        </v-form>

        <v-btn
          class="mt-4"
          block
          size="large"
          color="primary"
          :loading="loading"
          @click="login"
        >
          Login
        </v-btn>
      </v-card-text>
    </v-card>
  </div>
</template>
