<script setup lang="ts">
import KnowledgeUniverse from '@/components/universe/KnowledgeUniverse.vue'
import KnowledgePanel from '@/components/knowledge/KnowledgePanel.vue'
import UserChip from '@/components/user/UserChip.vue'
import ProfileDrawer from '@/components/user/ProfileDrawer.vue'
import FloatingBall from '@/components/ai/FloatingBall.vue'
import AgentPanel from '@/components/ai/AgentPanel.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>

<template>
  <main class="app-root">
    <!-- Layer 0: 3D Universe (Base Canvas) -->
    <KnowledgeUniverse />

    <!-- Layer 1: 2D Knowledge Panel (Slide from right) -->
    <KnowledgePanel />

    <!-- Layer 2 & 4: User Profile (Bottom left) -->
    <UserChip />
    <ProfileDrawer />

    <!-- Layer 3 & 4: AI Agent (Bottom right) -->
    <FloatingBall />
    <AgentPanel />

    <!-- Global Notifications (Optional Overlay) -->
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
.app-root {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background-color: #02040a; /* Fallback for 3D canvas */
}

/* Toast Notifications */
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

/* Transition for toasts */
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
