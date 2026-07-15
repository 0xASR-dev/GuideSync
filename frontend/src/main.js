import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Bootstrap CSS + JS (for navbar toggler, etc.)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
// GuideSync theme (must come after Bootstrap so it overrides)
import './assets/theme.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
