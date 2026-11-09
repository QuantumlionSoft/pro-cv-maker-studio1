import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import '@fontsource-variable/manrope'
import './assets/css/app.css'
import 'bootstrap' // enables Bootstrap's data-API (collapse, accordion) and JS components
import App from './App.vue'
import router from './router'

createApp(App).use(createPinia()).use(router).mount('#app')
