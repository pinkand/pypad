<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// Dummy data for unread counts
const unreadMessages = 2
const unreadNotifications = 3
const totalUnread = unreadMessages + unreadNotifications
</script>

<template>
  <button 
    class="user-chip glass"
    :class="{ 'is-active': appStore.profileOpen }"
    @click="appStore.toggleProfile()"
  >
    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User Avatar" class="avatar" />
    
    <div v-if="totalUnread > 0" class="badge">
      {{ totalUnread > 99 ? '99+' : totalUnread }}
    </div>
  </button>
</template>

<style scoped>
.user-chip {
  position: absolute;
  bottom: 32px;
  left: 32px;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
}

.user-chip:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.user-chip.is-active {
  box-shadow: 0 0 0 2px var(--accent), 0 4px 12px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background-color: var(--bg-tertiary);
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: var(--danger);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid rgba(15, 10, 40, 0.8);
  box-sizing: content-box;
}
</style>
