<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const launchWorkspace = () => {
  appStore.openWorkspace('code')
  appStore.toggleAgent() // Optional: close agent panel if wanted
}
</script>

<template>
  <div class="flex flex-col h-full items-center justify-center p-8 text-center">
    <div class="glass-launcher">
      <div class="launcher-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="14 2 14 8 20 8" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 13h2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 17h2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M14 13h2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M14 17h2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3 class="launcher-title">AI Coding Workspace</h3>
      <p class="launcher-desc">Immersive environment with Monaco Editor, AI Tutor, and real-time execution.</p>
      
      <button class="launch-btn" @click="launchWorkspace">
        Enter Workspace
      </button>
    </div>
  </div>
</template>

<style scoped>
.glass-launcher {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 20px;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
}

.launcher-icon {
  color: var(--status-learning);
  margin-bottom: 16px;
}

.launcher-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.launcher-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 24px;
}

.launch-btn {
  background: var(--text-primary);
  color: #fff;
  border: none;
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.launch-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}
</style>