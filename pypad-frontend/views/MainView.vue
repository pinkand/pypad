<script setup lang="ts">
import KnowledgeUniverse from '@/components/universe/KnowledgeUniverse.vue'
import KnowledgePanel from '@/components/knowledge/KnowledgePanel.vue'
import LearningGuidePanel from '@/components/knowledge/LearningGuidePanel.vue'
import UserChip from '@/components/user/UserChip.vue'
import ProfileDrawer from '@/components/user/ProfileDrawer.vue'
import FloatingBall from '@/components/ai/FloatingBall.vue'
import AgentPanel from '@/components/ai/AgentPanel.vue'
import CodingWorkspace from '@/components/workspace/CodingWorkspace.vue'
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useCourseStore } from '@/stores/course'
import { onMounted, watch } from 'vue'

import { useRoute, useRouter } from 'vue-router'

// 仅负责 Top Level Page Dispatch & Store Core Bootstrapping
const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()
const courseStore = useCourseStore()
const route = useRoute()
const router = useRouter()

// Auto remove notifications after 3 seconds
watch(() => appStore.notifications.length, () => {
  if (appStore.notifications.length > 0) {
    const latest = appStore.notifications[appStore.notifications.length - 1]
    setTimeout(() => {
      appStore.removeNotification(latest.id)
    }, 3000)
  }
})

onMounted(async () => {
  await Promise.all([
    knowledgeStore.loadData(),
    courseStore.fetchCourses()
  ])

  // Restore node selection from URL query ?nodeId=xxx
  if (route.query.nodeId && typeof route.query.nodeId === 'string') {
    const targetNodeId = route.query.nodeId
    knowledgeStore.selectNode(targetNodeId)
    appStore.openPanel(targetNodeId)
  }
})

// Sync active node panel state to URL query string
watch(() => appStore.panelNodeId, (newNodeId) => {
  const query = { ...route.query }
  if (newNodeId) {
    query.nodeId = newNodeId
  } else {
    delete query.nodeId
  }
  router.replace({ query }).catch(() => {})
})
</script>

<template>
  <main class="app-root" :class="{ 'cosmic-bg': appStore.bgAnimationStyle === 'cosmic' }">
    <!-- Layer 0: 3D Universe (Transparent Canvas over particles) -->
    <KnowledgeUniverse />

    <!-- Layer 1: AI Learning Guide (Left Sidebar) -->
    <LearningGuidePanel />

    <!-- Layer 2: 2D Knowledge Panel (Slide from right) -->
    <KnowledgePanel />

    <!-- Layer 2 & 4: User Profile (Bottom left) -->
    <UserChip />
    <ProfileDrawer />

    <!-- Layer 3 & 4: AI Agent (Bottom right) -->
    <FloatingBall />
    <AgentPanel />

    <!-- Layer 5: Coding Workspace (Full overlay) -->
    <CodingWorkspace />

    <!-- Global Notifications Overlay -->
    <div class="notifications-container">
      <TransitionGroup name="notif">
        <div 
          v-for="notif in appStore.notifications" 
          :key="notif.id" 
          class="toast-notification glass"
          :class="`toast-${notif.type}`"
        >
          {{ notif.message }}
        </div>
      </TransitionGroup>
    </div>
  </main>
</template>

<style scoped>
@keyframes ambient-glow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.app-root {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background-color: var(--bg-primary);
  transition: background 0.5s ease;
}

.app-root.cosmic-bg {
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.10) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(56, 189, 248, 0.10) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.06) 0%, transparent 50%);
  background-size: 200% 200%;
  animation: ambient-glow 16s ease infinite;
}

.notifications-container {
  position: absolute;
  top: 32px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 100;
  pointer-events: none;
}

.toast-notification {
  padding: 12px 24px;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 600;
  pointer-events: auto;
  box-shadow: var(--shadow-md);
  text-align: center;
}

.toast-info { border-left: 4px solid var(--blue-primary); }
.toast-success { border-left: 4px solid var(--success); }
.toast-warning { border-left: 4px solid var(--warning); }
.toast-error { border-left: 4px solid var(--danger); }

.notif-enter-active,
.notif-leave-active {
  transition: all 0.3s ease;
}
.notif-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}
.notif-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}
</style>
