<script setup lang="ts">
import KnowledgeUniverse from '@/components/universe/KnowledgeUniverse.vue'
import KnowledgeMap from '@/components/map/KnowledgeMap.vue'
import KnowledgePanel from '@/components/knowledge/KnowledgePanel.vue'
import LearningGuidePanel from '@/components/knowledge/LearningGuidePanel.vue'
import UserChip from '@/components/user/UserChip.vue'
import ProfileDrawer from '@/components/user/ProfileDrawer.vue'
import SettingsDrawer from '@/components/common/SettingsDrawer.vue'
import FloatingBall from '@/components/ai/FloatingBall.vue'
import AgentPanel from '@/components/ai/AgentPanel.vue'
import CodingWorkspace from '@/components/workspace/CodingWorkspace.vue'
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useCourseStore } from '@/stores/course'
import { ref, onMounted, watch } from 'vue'

import { useRoute, useRouter } from 'vue-router'

// 仅负责 Top Level Page Dispatch & Store Core Bootstrapping
const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()
const courseStore = useCourseStore()
const route = useRoute()
const router = useRouter()

// 2D/3D 视图切换
const viewMode = ref<'3d' | '2d'>('3d')
const toggleViewMode = () => {
  viewMode.value = viewMode.value === '3d' ? '2d' : '3d'
}

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
    <!-- Layer 0: 3D Universe or 2D Map (based on viewMode toggle) -->
    <KnowledgeUniverse v-if="viewMode === '3d'" />
    <div v-else class="map-view-container">
      <KnowledgeMap />
    </div>

    <!-- 2D/3D 视图切换按钮 (右上角) -->
    <div class="view-toggle-wrapper">
      <button class="view-toggle-btn glass" :class="{ active: viewMode === '2d' }" @click="toggleViewMode">
        <span class="toggle-label" :class="{ 'label-active': viewMode === '3d' }">3D</span>
        <span class="toggle-track">
          <span class="toggle-thumb" :class="{ 'thumb-right': viewMode === '2d' }"></span>
        </span>
        <span class="toggle-label" :class="{ 'label-active': viewMode === '2d' }">2D</span>
      </button>
    </div>

    <!-- Layer 1: AI Learning Guide (Left Sidebar) -->
    <LearningGuidePanel />

    <!-- Layer 2: 2D Knowledge Panel (Slide from right) -->
    <KnowledgePanel />

    <!-- Layer 2 & 4: User Profile (Bottom left) -->
    <UserChip />
    <ProfileDrawer />

    <!-- Layer 3 & 4: Settings & AI Agent (Bottom right) -->
    <SettingsDrawer />
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

/* 2D Map View Container */
.map-view-container {
  width: 100vw;
  height: 100vh;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

/* 2D/3D View Toggle */
.view-toggle-wrapper {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 50;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: var(--shadow-md);
  user-select: none;
}

.view-toggle-btn:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-1px);
}

.view-toggle-btn:active {
  transform: scale(0.97);
}

.toggle-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  transition: color 0.2s ease;
  letter-spacing: 0.5px;
}

.label-active {
  color: var(--text-primary);
}

.toggle-track {
  width: 36px;
  height: 20px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  position: relative;
  transition: background 0.3s ease;
}

.view-toggle-btn.active .toggle-track {
  background: var(--accent);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.thumb-right {
  transform: translateX(16px);
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
