import { createVuetify } from 'vuetify'

import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    theme: {
      defaultTheme: 'dark',
      themes: {
        light: {
          dark: false,
          colors: {
            'primary': 'rgba(142, 147, 108, 1)',
            'secondary': 'rgba(113, 108, 147, 1)',
            'primary-transparent': 'rgba(142, 147, 108, 0.25)',
            'secondary-transparent': 'rgba(113, 108, 147, 0.25)',
          },
        },
        dark: {
          dark: true,
          colors: {
            'primary': 'rgba(142, 147, 108, 1)',
            'secondary': 'rgba(113, 108, 147, 1)',
            'primary-transparent': 'rgba(142, 147, 108, 0.25)',
            'secondary-transparent': 'rgba(113, 108, 147, 0.25)',
          },
        },
      },
    },
    defaults: {
      VTextField: {
        variant: 'outlined',
      },
      VAutocomplete: {
        variant: 'outlined',
      },
      VSelect: {
        variant: 'outlined',
      },
      VBtn: {
        variant: 'outlined',
      },
      VContainer: {
        style: 'max-width: 1400px',
      },
      VCard: {
        rounded: 'lg',
        width: '100%',
      },
      VTab: {
        rounded: 'xl',
      },
      VListItem: {
        rounded: 'lg',
      },
    },
    display: {
      mobileBreakpoint: 'sm',
    },
  })
  app.vueApp.use(vuetify)
})
