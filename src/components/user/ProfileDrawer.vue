<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import { computed } from 'vue'

const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()

const overallProgress = computed(() => {
  const nodes = knowledgeStore.nodes
  if (nodes.length === 0) return 0
  const totalMastery = nodes.reduce((sum, n) => sum + (knowledgeStore.getNodeMastery(n.id) || 0), 0)
  return Math.round(totalMastery / nodes.length)
})

const handleLogout = () => {
  console.log('logout')
}
</script>

<template>
  <Transition name="slide-fade-up">
    <div v-if="appStore.profileOpen" class="profile-drawer glass">
      
      <!-- Header -->
      <div class="drawer-header">
        <div class="user-info">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" class="avatar-large" />
          <div class="user-details">
            <h2 class="username">Alex Developer</h2>
            <span class="level">Level 12 Explorer</span>
          </div>
        </div>
        <button class="close-btn" @click="appStore.toggleProfile()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="drawer-content">
        <!-- Progress -->
        <section class="section">
          <h3 class="section-title">Cognitive Progress</h3>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ width: `${overallProgress}%` }"></div>
          </div>
          <div class="progress-text">
            <span>Overall Mastery</span>
            <span class="font-mono">{{ overallProgress }}%</span>
          </div>
        </section>

        <!-- Notifications -->
        <section class="section">
          <div class="flex-between">
            <h3 class="section-title">Notifications</h3>
            <span class="badge" v-if="appStore.notifications.length">{{ appStore.notifications.length }}</span>
          </div>
          
          <div v-if="appStore.notifications.length === 0" class="empty-state">
            No new notifications
          </div>
          
          <ul class="notification-list" v-else>
            <li v-for="notif in appStore.notifications.slice(0, 3)" :key="notif.id" class="notif-item">
              <span class="notif-dot" :class="`notif-${notif.type}`"></span>
              <p class="notif-msg">{{ notif.message }}</p>
            </li>
          </ul>
        </section>

        <!-- Settings -->
        <section class="section">
          <h3 class="section-title">Settings</h3>
          <button class="menu-btn" @click="appStore.toggleTheme()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path v-if="appStore.isDark" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              <path v-else d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            {{ appStore.isDark ? 'Light Mode' : 'Dark Mode' }}
          </button>
          <button class="menu-btn text-danger" @click="handleLogout">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </section>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.profile-drawer {
  position: absolute;
  bottom: 96px; /* above the chip */
  left: 32px;
  width: 320px;
  border-radius: var(--radius-xl);
  z-index: 40;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: calc(100vh - 128px);
}

.drawer-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--border);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-large {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--bg-tertiary);
  border: 2px solid var(--border);
}

.username {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.level {
  font-size: 13px;
  color: var(--blue-primary);
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.drawer-content {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  font-weight: 700;
  margin-bottom: 12px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* Progress */
.progress-bar-bg {
  height: 8px;
  background-color: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-bar-fill {
  height: 100%;
  background-color: var(--blue-primary);
  border-radius: 4px;
  transition: width 1s ease-out;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
}

/* Notifications */
.badge {
  background: var(--blue-light);
  color: var(--blue-active);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
}

.empty-state {
  font-size: 13px;
  color: var(--text-tertiary);
  font-style: italic;
}

.notification-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notif-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.notif-info { background-color: var(--blue-primary); }
.notif-success { background-color: var(--success); }
.notif-warning { background-color: var(--warning); }
.notif-error { background-color: var(--danger); }

.notif-msg {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
}

/* Settings */
.menu-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  text-align: left;
  margin-bottom: 4px;
}

.menu-btn:hover {
  background: var(--bg-tertiary);
}

.text-danger {
  color: var(--danger);
}
.text-danger:hover {
  background: rgba(196, 154, 154, 0.1);
}

/* Transitions */
.slide-fade-up-enter-active,
.slide-fade-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom left;
}

.slide-fade-up-enter-from,
.slide-fade-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
