<script setup lang="ts">
import { computed, ref } from 'vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useAppStore } from '@/stores/app'
import { MASTERY_THRESHOLDS } from '@/utils/constants'

const knowledgeStore = useKnowledgeStore()
const appStore = useAppStore()

const isCollapsed = ref(false)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// Mastery overview computation
const masteryStats = computed(() => {
  const stats = {
    mastered: 0,
    learning: 0,
    weak: 0,
    unlearned: 0,
    total: knowledgeStore.nodes.length
  }
  
  knowledgeStore.nodes.forEach(node => {
    const mastery = knowledgeStore.getNodeMastery(node.id) || 0
    if (mastery >= MASTERY_THRESHOLDS.excellent) stats.mastered++
    else if (mastery >= MASTERY_THRESHOLDS.good) stats.learning++
    else if (mastery >= MASTERY_THRESHOLDS.weak) stats.weak++
    else stats.unlearned++
  })
  
  return stats
})

// Recommendations logic
const recommendations = computed(() => {
  // Find unlearned or weak nodes where ALL hard prerequisites are met (>= 60 mastery)
  const available = knowledgeStore.nodes.filter(node => {
    const mastery = knowledgeStore.getNodeMastery(node.id) || 0
    if (mastery >= MASTERY_THRESHOLDS.good) return false // Already learning/mastered
    
    // Check prerequisites
    const prereqEdges = knowledgeStore.edges.filter(e => e.target === node.id && e.relationType === 'prerequisite' && e.strength === 'hard')
    const allMet = prereqEdges.every(e => {
      const parentMastery = knowledgeStore.getNodeMastery(e.source) || 0
      return parentMastery >= MASTERY_THRESHOLDS.good
    })
    
    return allMet
  })
  
  // Sort by importance (highest first) and take top 3
  return available.sort((a, b) => (b.importance || 0) - (a.importance || 0)).slice(0, 3)
})

// Weak nodes (Needs review)
const weakNodes = computed(() => {
  return knowledgeStore.weakNodes
    .filter(n => (knowledgeStore.getNodeMastery(n.id) || 0) > 0) // Exclude completely unlearned
    .sort((a, b) => (knowledgeStore.getNodeMastery(a.id) || 0) - (knowledgeStore.getNodeMastery(b.id) || 0))
    .slice(0, 3)
})

const openNode = (nodeId: string) => {
  appStore.openPanel(nodeId)
}
</script>

<template>
  <Transition name="fade-in">
    <div v-if="!appStore.panelOpen" class="learning-guide-wrapper" :class="{ collapsed: isCollapsed }">
      
      <div class="learning-guide-panel glass">
      
      <div class="panel-section">
        <h3 class="section-title">学习状态</h3>
        <div class="stat-row">
          <span class="stat-label"><span class="status-dot mastered"></span>已掌握</span>
          <span class="stat-value">{{ masteryStats.mastered }}/{{ masteryStats.total }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label"><span class="status-dot learning"></span>学习中</span>
          <span class="stat-value">{{ masteryStats.learning }}/{{ masteryStats.total }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label"><span class="status-dot weak"></span>薄弱</span>
          <span class="stat-value">{{ masteryStats.weak }}/{{ masteryStats.total }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label"><span class="status-dot unlearned"></span>未学习</span>
          <span class="stat-value">{{ masteryStats.unlearned }}/{{ masteryStats.total }}</span>
        </div>
      </div>

      <div class="panel-section" v-if="recommendations.length > 0">
        <h3 class="section-title">推荐学习路径</h3>
        <ul class="node-list">
          <li 
            v-for="node in recommendations" 
            :key="node.id"
            class="node-item"
            @click="openNode(node.id)"
          >
            <div class="item-main">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--info)" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
              <span class="node-name">{{ node.name }}</span>
            </div>
            <span class="node-cat">{{ node.category }}</span>
          </li>
        </ul>
      </div>

      <div class="panel-section" v-if="weakNodes.length > 0">
        <h3 class="section-title">需要复习</h3>
        <ul class="node-list">
          <li 
            v-for="node in weakNodes" 
            :key="node.id"
            class="node-item warning"
            @click="openNode(node.id)"
          >
            <div class="item-main">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" stroke-width="2">
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <span class="node-name">{{ node.name }}</span>
            </div>
            <span class="node-cat">{{ knowledgeStore.getNodeMastery(node.id) }}%</span>
          </li>
        </ul>
      </div>

      </div>

      <button class="toggle-btn glass" @click="toggleCollapse">
        <svg v-if="!isCollapsed" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>

    </div>
  </Transition>
</template>

<style scoped>
.learning-guide-wrapper {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) translateX(32px);
  z-index: 30;
  display: flex;
  align-items: center;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.learning-guide-wrapper.collapsed {
  transform: translateY(-50%) translateX(calc(-100% + 24px));
}

.learning-guide-panel {
  width: 280px;
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toggle-btn {
  width: 24px;
  height: 48px;
  border: 1px solid var(--border);
  border-left: none;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
  padding: 0;
  margin-left: -1px;
}

.toggle-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 8px;
}

.stat-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-weight: 500;
}

.stat-value {
  font-family: var(--font-mono);
  color: var(--text-secondary);
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.mastered { background-color: var(--status-mastered); }
.status-dot.learning { background-color: var(--status-learning); }
.status-dot.weak { background-color: var(--status-weak); }
.status-dot.unlearned { background-color: var(--status-unlearned); border: 1px solid var(--border); }

.node-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.node-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.node-item:hover {
  background: var(--bg-secondary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  border-color: var(--border-hover);
}

.item-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.node-cat {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
}

.node-item.warning:hover {
  border-color: var(--warning);
}


.fade-in-enter-active,
.fade-in-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-in-enter-from,
.fade-in-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(12px);
}
</style>
