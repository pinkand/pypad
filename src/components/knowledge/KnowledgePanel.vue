<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import KnowledgeMap from '@/components/map/KnowledgeMap.vue'
import { computed } from 'vue'

const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()

const activeNode = computed(() => {
  if (!appStore.panelNodeId) return null
  return knowledgeStore.getNodeById(appStore.panelNodeId)
})

const handleAiExplain = () => {
  if (activeNode.value) {
    appStore.openAgentWithAction('explain', activeNode.value.id)
  }
}

const handlePractice = () => {
  if (activeNode.value) {
    appStore.openAgentWithAction('practice', activeNode.value.id)
  }
}
</script>

<template>
  <Transition name="slide-in-right">
    <div v-if="appStore.panelOpen" class="knowledge-panel glass">
      
      <!-- Header -->
      <div class="panel-header">
        <div>
          <h2 class="node-title">{{ activeNode?.name || 'Knowledge Graph' }}</h2>
          <span class="node-category">{{ activeNode?.category || 'Learning Path' }}</span>
        </div>
        <button class="close-btn" @click="appStore.closePanel()">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Graph Container (2D) -->
      <div class="graph-container">
        <!-- We reuse the existing map, it should adapt to this container -->
        <KnowledgeMap />
      </div>

      <!-- Footer Actions -->
      <div class="panel-footer">
        <button class="btn btn-primary" @click="handleAiExplain">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.792 0-5.484-.14-8.135-.411-1.718-.293-2.3-2.379-1.067-3.61l1.402-1.402M8.25 12h7.5" />
          </svg>
          AI Explain
        </button>
        <button class="btn btn-secondary" @click="handlePractice">
          Generate Practice
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.knowledge-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 50vw;
  min-width: 600px;
  max-width: 800px;
  height: 100vh;
  border-radius: var(--radius-xl) 0 0 var(--radius-xl);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: -10px 0 40px rgba(0,0,0,0.05);
}

.panel-header {
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.8);
  border-top-left-radius: inherit;
  border-top-right-radius: inherit;
}

.node-title {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.node-category {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* Override map internal styles if needed */
:deep(.vue-flow-wrapper) {
  height: 100%;
}
:deep(.map-container) {
  height: 100%;
  border-radius: 0;
  border: none;
  background: transparent !important;
}

.panel-footer {
  padding: 24px 32px;
  border-top: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  gap: 16px;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  border: none;
}

.btn-primary {
  background-color: var(--accent);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background-color: var(--accent-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background-color: var(--border-hover);
}

/* Transitions */
.slide-in-right-enter-active,
.slide-in-right-leave-active {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s;
}

.slide-in-right-enter-from,
.slide-in-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
