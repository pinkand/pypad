import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { clearStorage } from './utils/storage'

// Auto clear stale browser cache from previous versions
const CURRENT_DATA_VERSION = '2.0-textbook-v1'
if (localStorage.getItem('pypad:data_version') !== CURRENT_DATA_VERSION) {
  clearStorage()
  localStorage.setItem('pypad:data_version', CURRENT_DATA_VERSION)
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
