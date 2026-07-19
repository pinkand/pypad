<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'
import ChatWindow from '@/components/agent/ChatWindow.vue'
import TaskPanel from '@/components/agent/TaskPanel.vue'
import CodeEditor from '@/components/agent/CodeEditor.vue'

const appStore = useAppStore()
const activeTab = ref<'chat' | 'task' | 'code'>('chat')

const tabs = [
  { id: 'chat', label: 'Chat' },
  { id: 'task', label: 'Tasks' },
  { id: 'code', label: 'Code' }
] as const
</script>

<template>
  <Transition name="slide-fade-up">
    <div v-if="appStore.agentOpen" class="agent-panel glass">
      
      <!-- Header -->
      <div class="panel-header">
        <div class="tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>
        <button class="close-btn" @click="appStore.toggleAgent()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="panel-content">
        <div v-show="activeTab === 'chat'" class="tab-pane">
          <ChatWindow />
        </div>
        <div v-show="activeTab === 'task'" class="tab-pane">
          <TaskPanel />
        </div>
        <div v-show="activeTab === 'code'" class="tab-pane">
          <CodeEditor />
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.agent-panel {
  position: absolute;
  bottom: 96px; /* above the floating ball */
  right: 32px;
  width: 420px;
  height: 600px;
  border-radius: var(--radius-xl);
  z-index: 40;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-glass);
}

.panel-header {
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  background: rgba(245, 243, 240, 0.4);
}

.tabs {
  display: flex;
  gap: 8px;
  background: var(--border);
  padding: 4px;
  border-radius: var(--radius-lg);
}

.tab-btn {
  padding: 6px 16px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--bg-primary);
  color: var(--blue-active);
  box-shadow: var(--shadow-sm);
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

.panel-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.tab-pane {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
}

/* Ensure child components stretch */
:deep(.chat-container),
:deep(.task-container),
:deep(.code-container) {
  height: 100%;
  border-radius: 0;
  background: transparent !important;
  border: none;
}

/* Transitions */
.slide-fade-up-enter-active,
.slide-fade-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom right;
}

.slide-fade-up-enter-from,
.slide-fade-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
