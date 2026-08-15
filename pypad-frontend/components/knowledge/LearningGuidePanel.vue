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

// 11个教材项目定义
const TEXTBOOK_PROJECTS = [
  { id: 'chap-1', name: '项目1：猜价赢大奖', description: 'Python开发环境搭建与编程规范', icon: '🎯' },
  { id: 'chap-2', name: '项目2：简单计算器', description: '基本输入输出、数据类型与运算符', icon: '🔢' },
  { id: 'chap-3', name: '项目3：健康数据分析', description: '条件分支与循环控制流结构', icon: '❤️' },
  { id: 'chap-4', name: '项目4：词语踪迹寻觅', description: '字符串处理、检索与切片操作', icon: '🔍' },
  { id: 'chap-5', name: '项目5：核心价值观问答', description: '列表与元组容器数据结构', icon: '📚' },
  { id: 'chap-6', name: '项目6：公益图书角管理', description: '函数定义、参数传递与模块化设计', icon: '📖' },
  { id: 'chap-7', name: '项目7：校园热点话题统计', description: '字典与集合的高效查找与统计', icon: '📊' },
  { id: 'chap-8', name: '项目8：天气预报应用', description: '模块化开发、内置标准库与第三方包', icon: '🌤️' },
  { id: 'chap-9', name: '项目9：个人财务管理', description: '面向对象编程 (OOP) 核心理念', icon: '💰' },
  { id: 'chap-10', name: '项目10：销售数据分析', description: '文件 I/O 操作与数据持久化存储', icon: '📁' },
  { id: 'chap-11', name: '项目11：肺活量监测', description: '异常捕获处理与程序健壮性设计', icon: '🫁' },
]

// 分类到章节的映射
const CATEGORY_TO_CHAPTER: Record<string, string> = {
  '基础环境': 'chap-1',
  '基本语法': 'chap-2',
  '控制结构': 'chap-3',
  '数据结构': 'chap-4',
  '函数设计': 'chap-6',
  '模块与架构': 'chap-8',
  '面向对象': 'chap-9',
  '文件与数据': 'chap-10',
  '健壮性': 'chap-11',
}

// 节点到章节的特殊覆盖（字典/集合属于chap-7）
const NODE_CHAPTER_OVERRIDE: Record<string, string> = {
  'dict-basic': 'chap-7',
  'dict-methods': 'chap-7',
  'set-basic': 'chap-7',
}

// 获取节点所属章节
const getNodeChapter = (node: any): string => {
  if (NODE_CHAPTER_OVERRIDE[node.id]) return NODE_CHAPTER_OVERRIDE[node.id]
  return CATEGORY_TO_CHAPTER[node.category] || 'chap-2'
}

// 计算每个项目的进度
const projectProgress = computed(() => {
  const chapterMastery: Record<string, { total: number; count: number }> = {}
  
  // 初始化
  TEXTBOOK_PROJECTS.forEach(p => {
    chapterMastery[p.id] = { total: 0, count: 0 }
  })
  
  // 只统计叶子节点（非domain节点）
  knowledgeStore.nodes.forEach(node => {
    if (node.category === 'Root' || node.category === 'Domain') return
    const chapterId = getNodeChapter(node)
    if (chapterMastery[chapterId]) {
      const mastery = knowledgeStore.getNodeMastery(node.id) || 0
      chapterMastery[chapterId].total += mastery
      chapterMastery[chapterId].count++
    }
  })
  
  return TEXTBOOK_PROJECTS.map(project => {
    const data = chapterMastery[project.id]
    const avgMastery = data.count > 0 ? Math.round(data.total / data.count) : 0
    return {
      ...project,
      mastery: avgMastery,
      nodeCount: data.count,
      status: avgMastery >= MASTERY_THRESHOLDS.excellent ? 'mastered' 
        : avgMastery >= MASTERY_THRESHOLDS.good ? 'learning' 
        : avgMastery > 0 ? 'weak' : 'unlearned'
    }
  })
})

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
    if (node.category === 'Root' || node.category === 'Domain') return
    const mastery = knowledgeStore.getNodeMastery(node.id) || 0
    if (mastery >= MASTERY_THRESHOLDS.excellent) stats.mastered++
    else if (mastery >= MASTERY_THRESHOLDS.good) stats.learning++
    else if (mastery >= MASTERY_THRESHOLDS.weak) stats.weak++
    else stats.unlearned++
  })
  
  stats.total = stats.mastered + stats.learning + stats.weak + stats.unlearned
  return stats
})

// Recommendations logic
const recommendations = computed(() => {
  // Find unlearned or weak nodes where ALL hard prerequisites are met (>= 60 mastery)
  const available = knowledgeStore.nodes.filter(node => {
    if (node.category === 'Root' || node.category === 'Domain') return false
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
    .filter(n => n.category !== 'Root' && n.category !== 'Domain')
    .filter(n => (knowledgeStore.getNodeMastery(n.id) || 0) > 0) // Exclude completely unlearned
    .sort((a, b) => (knowledgeStore.getNodeMastery(a.id) || 0) - (knowledgeStore.getNodeMastery(b.id) || 0))
    .slice(0, 3)
})

const openNode = (nodeId: string) => {
  appStore.openPanel(nodeId)
}

const openProject = (chapterId: string) => {
  // 打开该项目下的第一个节点
  const projectNodes = knowledgeStore.nodes.filter(n => {
    if (n.category === 'Root' || n.category === 'Domain') return false
    return getNodeChapter(n) === chapterId
  })
  if (projectNodes.length > 0) {
    // 按sortOrder排序，打开第一个
    const sorted = projectNodes.sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
    appStore.openPanel(sorted[0].id)
  }
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  switch (status) {
    case 'mastered': return 'var(--status-mastered)'
    case 'learning': return 'var(--status-learning)'
    case 'weak': return 'var(--status-weak)'
    default: return 'var(--status-unlearned)'
  }
}
</script>

<template>
  <Transition name="fade-in">
    <div v-if="!appStore.panelOpen" class="learning-guide-wrapper" :class="{ collapsed: isCollapsed }">
      
      <div class="learning-guide-panel glass">
      
      <!-- 学习状态概览 -->
      <div class="panel-section">
        <h3 class="section-title">📊 学习状态</h3>
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

      <!-- 教材项目列表 -->
      <div class="panel-section">
        <h3 class="section-title">📚 教材项目</h3>
        <div class="project-scroll">
          <ul class="project-list">
            <li 
              v-for="project in projectProgress" 
              :key="project.id"
              class="project-item"
              @click="openProject(project.id)"
            >
              <div class="project-header">
                <span class="project-icon">{{ project.icon }}</span>
                <span class="project-name">{{ project.name }}</span>
              </div>
              <div class="project-progress">
                <div class="progress-bar-bg">
                  <div 
                    class="progress-bar-fill" 
                    :style="{ width: project.mastery + '%', backgroundColor: getStatusColor(project.status) }"
                  ></div>
                </div>
                <span class="progress-text" :style="{ color: getStatusColor(project.status) }">{{ project.mastery }}%</span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 推荐学习 -->
      <div class="panel-section" v-if="recommendations.length > 0">
        <h3 class="section-title">🎯 推荐学习</h3>
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

      <!-- 需要复习 -->
      <div class="panel-section" v-if="weakNodes.length > 0">
        <h3 class="section-title">⚠️ 需要复习</h3>
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
  width: 300px;
  max-height: 85vh;
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
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
  background: var(--bg-primary);
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

/* 学习状态统计 */
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

/* 教材项目列表 */
.project-scroll {
  max-height: 350px;
  overflow-y: auto;
  margin-right: -4px;
  padding-right: 4px;
}

.project-scroll::-webkit-scrollbar {
  width: 4px;
}

.project-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.project-scroll::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 2px;
}

.project-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.project-item {
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.project-item:hover {
  background: var(--bg-secondary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  border-color: var(--border-hover);
}

.project-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.project-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.project-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar-bg {
  flex: 1;
  height: 4px;
  background-color: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-text {
  font-size: 11px;
  font-family: var(--font-mono);
  width: 32px;
  text-align: right;
  font-weight: 600;
}

/* 推荐学习和复习节点 */
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
  flex: 1;
  min-width: 0;
}

.node-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-cat {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
  flex-shrink: 0;
}

.node-item.warning:hover {
  border-color: var(--warning);
}

/* 动画 */
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
