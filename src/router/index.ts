import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/universe'
    },
    {
      path: '/universe',
      name: 'universe',
      component: () => import('../views/universe/UniverseView.vue'),
      meta: { title: '知识宇宙' }
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('../views/map/MapView.vue'),
      meta: { title: '知识图谱' }
    },
    {
      path: '/map/:nodeId',
      name: 'map-node',
      component: () => import('../views/map/MapView.vue'),
      meta: { title: '知识图谱' }
    },
    {
      path: '/agent',
      name: 'agent',
      component: () => import('../views/agent/AgentView.vue'),
      meta: { title: 'AI学习助手' }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/dashboard/DashboardView.vue'),
      meta: { title: '学习仪表盘' }
    }
  ],
})

export default router
