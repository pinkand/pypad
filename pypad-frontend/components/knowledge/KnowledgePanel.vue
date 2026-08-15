<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import KnowledgeMap from '@/components/map/KnowledgeMap.vue'
import { useWorkspaceStore } from '@/stores/workspace'

const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()
const workspaceStore = useWorkspaceStore()

const showTextbook = ref(true)

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

const handleLoadCode = () => {
  if (activeNode.value?.aiSummary?.recommendedCodeSnippet) {
    workspaceStore.setCode(activeNode.value.aiSummary.recommendedCodeSnippet)
    appStore.openWorkspace('code')
  }
}
</script>

<template>
  <Transition name="fade-in-scale">
    <div v-if="appStore.panelOpen" class="knowledge-panel glass-fullscreen">
      
      <!-- Top Header -->
      <div class="panel-header">
        <div class="header-info">
          <h2 class="node-title">{{ activeNode?.name || 'Knowledge Graph' }}</h2>
          <span class="node-category">《Python程序设计项目化教程》 · {{ activeNode?.category || '基础' }}</span>
        </div>
        
        <div class="header-actions">
          <button class="toggle-textbook-btn" @click="showTextbook = !showTextbook">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            {{ showTextbook ? '收起教材卡片' : '展开教材卡片' }}
          </button>

          <button class="close-btn" @click="appStore.closePanel()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 100% Fullscreen Interactive Topology Map -->
      <div class="full-map-wrapper">
        <KnowledgeMap />
      </div>

      <!-- Floating Left Textbook Summary Card -->
      <Transition name="slide-fade-left">
        <div v-if="showTextbook" class="floating-textbook-card glass">
          <div v-if="activeNode?.aiSummary" class="textbook-section">
            <div class="textbook-card overview-card">
              <h3>📖 教材精讲与实战背景</h3>
              <p>{{ activeNode.aiSummary.overview }}</p>
            </div>

            <!-- Key Points -->
            <div v-if="activeNode.aiSummary.keyPoints?.length" class="textbook-card points-card">
              <h3>📌 核心知识要点</h3>
              <ul>
                <li v-for="(point, idx) in activeNode.aiSummary.keyPoints" :key="idx">
                  {{ point }}
                </li>
              </ul>
            </div>

            <!-- Common Pitfalls -->
            <div v-if="activeNode.aiSummary.commonPitfalls?.length" class="textbook-card pitfalls-card">
              <h3>⚠️ 踩坑避雷与注意事项</h3>
              <ul>
                <li v-for="(pitfall, idx) in activeNode.aiSummary.commonPitfalls" :key="idx">
                  {{ pitfall }}
                </li>
              </ul>
            </div>

            <!-- Textbook Code Snippet -->
            <div v-if="activeNode.aiSummary.recommendedCodeSnippet" class="textbook-card code-card">
              <div class="code-card-header">
                <h3>💻 教材项目实操代码</h3>
                <button class="btn-load-code" @click="handleLoadCode">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                  </svg>
                  载入 Monaco 工作区
                </button>
              </div>
              <pre class="code-preview"><code>{{ activeNode.aiSummary.recommendedCodeSnippet }}</code></pre>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Bottom Right Floating Footer Actions -->
      <div class="floating-panel-footer">
        <button class="btn btn-primary" @click="handleAiExplain">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.792 0-5.484-.14-8.135-.411-1.718-.293-2.3-2.379-1.067-3.61l1.402-1.402M8.25 12h7.5" />
          </svg>
          AI 导师精讲
        </button>
        <button class="btn btn-secondary" @click="handlePractice">
          生成实战练习
        </button>
      </div>

    </div>
  </Transition>
</template>

<style scoped>
.glass-fullscreen {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 60;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
}

.panel-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  z-index: 30;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.node-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.node-category {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-textbook-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.toggle-textbook-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--border-hover);
}

.close-btn {
  background: rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-full);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transform: scale(1.05);
}

/* 100% Fullscreen Map Container */
.full-map-wrapper {
  position: absolute;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}

/* Floating Left Textbook Drawer Card */
.floating-textbook-card {
  position: absolute;
  top: 90px;
  left: 32px;
  width: 440px;
  max-height: calc(100vh - 180px);
  overflow-y: auto;
  border-radius: var(--radius-xl);
  padding: 20px;
  z-index: 25;
  box-shadow: var(--shadow-lg);
}

.textbook-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.textbook-card {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: var(--shadow-sm);
}

.textbook-card h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.overview-card p {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.points-card ul, .pitfalls-card ul {
  padding-left: 18px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.points-card li, .pitfalls-card li {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
}

.pitfalls-card {
  border-left: 4px solid var(--warning);
  background: rgba(254, 243, 199, 0.4);
}

.code-card {
  background: #1e1e2e;
  color: #cdd6f4;
  border: 1px solid #313244;
}

.code-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.code-card-header h3 {
  color: #f5c2e7;
  margin-bottom: 0;
}

.btn-load-code {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 600;
  color: #89b4fa;
  background: rgba(137, 180, 250, 0.15);
  border: 1px solid rgba(137, 180, 250, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-load-code:hover {
  background: rgba(137, 180, 250, 0.3);
  transform: translateY(-1px);
}

.code-preview {
  font-family: var(--font-mono, monospace);
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  margin: 0;
  color: #a6e3a1;
}

/* Floating Bottom Footer Actions */
.floating-panel-footer {
  position: absolute;
  bottom: 28px;
  right: 32px;
  z-index: 30;
  display: flex;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-lg);
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
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
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background-color: var(--border-hover);
}

/* Transitions */
.fade-in-scale-enter-active,
.fade-in-scale-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-in-scale-enter-from,
.fade-in-scale-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

.slide-fade-left-enter-active,
.slide-fade-left-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-fade-left-enter-from,
.slide-fade-left-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
