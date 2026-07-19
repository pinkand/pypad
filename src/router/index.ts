import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: () => import('../views/MainView.vue'),
      meta: { title: 'Python Learning OS' }
    }
  ],
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title as string || 'Python Learning OS'
  next()
})

export default router
