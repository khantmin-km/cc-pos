/**
 * Main Entry Point
 * 
 * Initializes the Vue application with Pinia and Router.
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Create Vue application instance
const app = createApp(App)

// Add Pinia for state management
app.use(createPinia())

// Add Vue Router
app.use(router)

// Mount to DOM
app.mount('#app')
