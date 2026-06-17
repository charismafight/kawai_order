import { createApp } from 'vue'
import './style.css'
import naive from 'naive-ui'
import router from './router'
import App from './App.vue'

createApp(App).use(naive).use(router).mount('#app')
