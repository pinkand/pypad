<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useUserStore } from '@/stores/user'
import PerformanceMonitor from './components/common/PerformanceMonitor.vue'

const userStore = useUserStore()

onMounted(async () => {
  await userStore.restoreSession()
  // 登录成功后从后端同步数据
  if (userStore.isLoggedIn) {
    userStore.loadDashboardStats()
    userStore.loadStudyRecords()
  }
})
</script>

<template>
  <RouterView />
  <PerformanceMonitor />
</template>
