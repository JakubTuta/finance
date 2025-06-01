<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const router = useRouter()

const authStore = useAuthStore()
const { user, initLoading } = storeToRefs(authStore)

watch(initLoading, (newLoading) => {
  if (!newLoading && user.value)
    router.push('/panel')
}, { immediate: true })
</script>

<template>
  <v-app theme="dark">
    <v-main class="landing-container">
      <v-container
        fluid
        class="fill-height"
      >
        <v-row
          align="center"
          justify="center"
          class="fill-height"
        >
          <v-col
            cols="12"
            md="8"
            lg="6"
            xl="5"
          >
            <div class="landing-content text-center">
              <!-- App Icon/Logo -->
              <div class="app-icon mb-8">
                <v-icon
                  size="80"
                  color="primary"
                >
                  mdi-finance
                </v-icon>
              </div>

              <!-- Main Heading -->
              <h1 class="display-1 font-weight-bold gradient-text mb-4">
                Welcome to Finance
              </h1>

              <!-- Subtitle -->
              <p class="text-h6 text-grey-lighten-1 font-weight-light mb-6">
                A smart money management app that helps you track your spending and income
              </p>

              <!-- Feature highlights -->
              <v-row
                class="mb-8"
                justify="center"
              >
                <v-col
                  cols="12"
                  sm="4"
                  class="text-center"
                >
                  <v-icon
                    size="32"
                    color="primary"
                    class="mb-2"
                  >
                    mdi-chart-line
                  </v-icon>

                  <p class="text-body-2 text-grey-lighten-2">
                    Track Spending
                  </p>
                </v-col>

                <v-col
                  cols="12"
                  sm="4"
                  class="text-center"
                >
                  <v-icon
                    size="32"
                    color="primary"
                    class="mb-2"
                  >
                    mdi-robot
                  </v-icon>

                  <p class="text-body-2 text-grey-lighten-2">
                    AI-Powered Insights
                  </p>
                </v-col>

                <v-col
                  cols="12"
                  sm="4"
                  class="text-center"
                >
                  <v-icon
                    size="32"
                    color="primary"
                    class="mb-2"
                  >
                    mdi-piggy-bank
                  </v-icon>

                  <p class="text-body-2 text-grey-lighten-2">
                    Savings Opportunities
                  </p>
                </v-col>
              </v-row>

              <!-- CTA Buttons -->
              <div class="cta-section">
                <p class="text-body-1 text-grey-lighten-2 mb-4">
                  Ready to take control of your finances?
                </p>

                <div class="d-flex flex-column flex-sm-row justify-center gap-4">
                  <NuxtLink
                    to="/auth/register"
                    class="text-decoration-none"
                  >
                    <v-btn
                      size="large"
                      color="primary"
                      variant="elevated"
                      class="cta-button-primary px-8 py-3"
                      rounded="lg"
                    >
                      <v-icon
                        left
                        class="mr-2"
                      >
                        mdi-account-plus
                      </v-icon>
                      Get Started
                    </v-btn>
                  </NuxtLink>

                  <NuxtLink
                    to="/auth/login"
                    class="text-decoration-none"
                  >
                    <v-btn
                      size="large"
                      variant="outlined"
                      color="primary"
                      class="cta-button-secondary px-8 py-3"
                      rounded="lg"
                    >
                      <v-icon
                        left
                        class="mr-2"
                      >
                        mdi-login
                      </v-icon>
                      Sign In
                    </v-btn>
                  </NuxtLink>
                </div>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>

      <!-- Background decoration -->
      <div class="background-decoration">
        <div class="floating-shape shape-1" />

        <div class="floating-shape shape-2" />

        <div class="floating-shape shape-3" />
      </div>
    </v-main>
  </v-app>
</template>

<style scoped>
.landing-container {
  background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #1C2128 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.landing-content {
  position: relative;
  z-index: 2;
}

.app-icon {
  background: linear-gradient(135deg, #2196F3, #21CBF3);
  border-radius: 50%;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 8px 32px rgba(33, 150, 243, 0.3);
}

.gradient-text {
  background: linear-gradient(135deg, #2196F3, #21CBF3, #03DAC6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
}

.cta-button-primary {
  background: linear-gradient(135deg, #2196F3, #21CBF3) !important;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.4) !important;
  transition: all 0.3s ease !important;
}

.cta-button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(33, 150, 243, 0.6) !important;
}

.cta-button-secondary {
  border: 2px solid #2196F3 !important;
  transition: all 0.3s ease !important;
}

.cta-button-secondary:hover {
  background: rgba(33, 150, 243, 0.1) !important;
  transform: translateY(-2px);
}

.gap-4 {
  gap: 1rem;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #2196F3, #21CBF3);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #03DAC6, #00BCD4);
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #9C27B0, #E91E63);
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .app-icon {
    width: 100px;
    height: 100px;
  }

  .app-icon .v-icon {
    font-size: 60px !important;
  }

  .display-1 {
    font-size: 2.5rem !important;
  }

  .floating-shape {
    opacity: 0.05;
  }
}

/* Dark theme overrides */
.v-application.theme--dark {
  background: #0D1117 !important;
}

.v-container {
  padding: 2rem 1rem;
}
</style>
