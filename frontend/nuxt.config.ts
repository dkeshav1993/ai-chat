// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss'],
  // Disable path-prefix on component auto-imports so <ErrorState>, <HotelList> etc
  // resolve correctly regardless of which sub-directory they live in.
  components: [
    { path: '~/components', pathPrefix: false }
  ],
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  typescript: {
    strict: true
  },
  app: {
    head: {
      title: 'NexTrip AI — Hotel Discovery',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI-powered hotel discovery. Find your perfect stay with conversational search.' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap' }
      ]
    }
  }
})
