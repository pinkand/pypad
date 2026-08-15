import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: '登录' }
    },
    {
      path: '/',
      name: 'main',
      component: MainView,
      meta: { title: 'PyPad' }
    },
    {
      path: '/universe',
      name: 'universe',
      component: MainView,
      meta: { title: '知识宇宙' }
    },
    {
      path: '/map',
      name: 'map',
      component: MainView,
      meta: { title: '知识图谱' }
    },
    {
      path: '/map/:nodeId',
      name: 'map-node',
      component: MainView,
      meta: { title: '知识图谱' }
    },
    {
      path: '/agent',
      name: 'agent',
      component: MainView,
      meta: { title: 'AI学习助手' }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: MainView,
      meta: { title: '学习仪表盘' }
    }
  ],
})

export default router
