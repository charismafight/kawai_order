import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import UploadView from '../views/UploadView.vue'
import RecordsView from '../views/RecordsView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/upload'
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadView,
    meta: { title: '上传图片' }
  },
  {
    path: '/records',
    name: 'Records',
    component: RecordsView,
    meta: { title: '上传记录' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router