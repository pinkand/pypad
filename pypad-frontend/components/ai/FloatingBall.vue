<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useRouter } from 'vue-router'

const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()
const router = useRouter()

const showNavTags = ref(false)

// 快捷导航标签
const navTags = computed(() => {
  const weakCount = knowledgeStore.weakNodes.length
  return [
    { id: 'agent', label: 'AI 导师', icon: '🎓', action: () => { router.push('/agent'); showNavTags.value = false } },
    { id: 'workspace', label: '代码工作区', icon: '💻', action: () => { appStore.openWorkspace('code'); showNavTags.value = false } },
    { id: 'teach', label: '教材精讲', icon: '📖', action: () => { appStore.openWorkspace('teach'); showNavTags.value = false } },
    { id: 'practice', label: '实战练习', icon: '✏️', action: () => { router.push('/practice'); showNavTags.value = false } },
    { id: 'projects', label: '项目实战', icon: '🚀', action: () => { router.push('/projects'); showNavTags.value = false } },
    { id: 'weak', label: `薄弱点 (${weakCount})`, icon: '⚠️', action: () => {
      if (knowledgeStore.weakNodes.length > 0) {
        const node = knowledgeStore.weakNodes[0]
        appStore.openPanel(node.id)
      }
      showNavTags.value = false
    }},
    { id: 'dashboard', label: '学习统计', icon: '📊', action: () => { router.push('/dashboard'); showNavTags.value = false } },
    { id: 'settings', label: '设置', icon: '⚙️', action: () => { appStore.toggleSettings(); showNavTags.value = false } },
  ]
})

const toggleNav = () => {
  showNavTags.value = !showNavTags.value
}
</script>

<template>
  <div class="floating-ball-wrapper">
    <!-- 快捷导航标签 -->
    <Transition name="tags-pop">
      <div v-if="showNavTags" class="nav-tags">
        <button
          v-for="tag in navTags"
          :key="tag.id"
          class="nav-tag glass"
          @click="tag.action"
        >
          <span class="tag-icon">{{ tag.icon }}</span>
          <span class="tag-label">{{ tag.label }}</span>
        </button>
      </div>
    </Transition>

    <!-- 主悬浮球 -->
    <button 
      class="floating-ball glass"
      :class="{ 'is-active': appStore.agentOpen || showNavTags }"
      @click="toggleNav"
    >
      <div class="glow-effect"></div>
      <svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.792 0-5.484-.14-8.135-.411-1.718-.293-2.3-2.379-1.067-3.61l1.402-1.402M8.25 12h7.5" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.floating-ball-wrapper {
  position: absolute;
  bottom: 32px;
  right: 32px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

/* 快捷导航标签容器 */
.nav-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.nav-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-md);
  white-space: nowrap;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.nav-tag:hover {
  transform: translateX(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.95);
}

.tag-icon {
  font-size: 16px;
  line-height: 1;
}

.tag-label {
  line-height: 1;
}

/* 主悬浮球 */
.floating-ball {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
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

.floating-ball.is-active .icon {
  transform: rotate(45deg);
}

/* 标签弹出动画 */
.tags-pop-enter-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.tags-pop-leave-active {
  transition: all 0.2s ease-in;
}

.tags-pop-enter-from,
.tags-pop-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}
</style>
