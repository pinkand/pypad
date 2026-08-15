import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import CoursesView from '../views/CoursesView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import PracticeView from '../views/PracticeView.vue'
import AgentView from '../views/AgentView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import TextbooksView from '../views/TextbooksView.vue'

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
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: '学习仪表盘' }
    },
    {
      path: '/courses',
      name: 'courses',
      component: CoursesView,
      meta: { title: '课程中心' }
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectsView,
      meta: { title: '项目实战' }
    },
    {
      path: '/practice',
      name: 'practice',
      component: PracticeView,
      meta: { title: '练习中心' }
    },
    {
      path: '/agent',
      name: 'agent',
      component: AgentView,
      meta: { title: 'AI 导师' }
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: AnalyticsView,
      meta: { title: '学习分析' }
    },
    {
      path: '/textbooks',
      name: 'textbooks',
      component: TextbooksView,
      meta: { title: '教材管理' }
    },
  ],
})

export default router
