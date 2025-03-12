/* eslint-disable node/prefer-global/process */
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  app: {
    head: {
      title: 'Finance',
      meta: [
        { name: 'description', content: 'A smart money management app that helps you track your spending and income. Powered by AI to identify savings opportunities and improve your financial health.' },
      ],
    },
  },

  runtimeConfig: {
    public: {
      SERVER_URL: process.env.DOCKER === 'true'
        ? 'http://host.docker.internal:8000'
        : 'http://localhost:8000',
    },
  },

  build: {
    transpile: ['vuetify'],
  },

  modules: [
    '@vueuse/nuxt',
    '@unocss/nuxt',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        // eslint-disable-next-line ts/ban-ts-comment
        // @ts-expect-error
        config.plugins.push(vuetify({ autoImport: true }))
      })
    },
  ],

  imports: {
    autoImport: true,
    dirs: [
      'stores/**',
      'constants/**',
      'components/**',
      'helpers/**',
      'utils/**',
    ],
  },

  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },

  ssr: false,

  nitro: {
    preset: 'node-server',
    firebase: {
      gen: 2,
    },
  },

  typescript: {
    strict: true,
  },

  compatibilityDate: '2024-07-18',
})
