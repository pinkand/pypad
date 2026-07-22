<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// Dummy unread messages from agent
const unreadAgentMessages = 1
</script>

<template>
  <button 
    class="floating-ball glass"
    :class="{ 'is-active': appStore.agentOpen }"
    @click="appStore.toggleAgent()"
  >
    <div class="glow-effect"></div>
    <svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.792 0-5.484-.14-8.135-.411-1.718-.293-2.3-2.379-1.067-3.61l1.402-1.402M8.25 12h7.5" />
    </svg>
    
    <div v-if="unreadAgentMessages > 0 && !appStore.agentOpen" class="badge">
      {{ unreadAgentMessages }}
    </div>
  </button>
</template>

<style scoped>
.floating-ball {
  position: absolute;
  bottom: 32px;
  right: 32px;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
  border: 1px solid var(--border);
}

.glow-effect {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.02);
}

.icon {
  color: var(--text-primary);
  z-index: 2;
  transition: transform 0.3s;
}

.floating-ball:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.floating-ball:hover .icon {
  transform: scale(1.1);
}

.floating-ball.is-active {
  box-shadow: 0 0 0 2px var(--accent), 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: scale(0.9);
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
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
  border: 2px solid var(--bg-primary);
  box-sizing: content-box;
  z-index: 3;
}
</style>
