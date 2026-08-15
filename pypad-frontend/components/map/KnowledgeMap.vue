<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Node, Edge } from '@vue-flow/core'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import type { MiniMapNodeFunc } from '@vue-flow/minimap'
import { useKnowledgeStore } from '@/stores/knowledge'
import MapNode from './MapNode.vue'
import MapEdge from './MapEdge.vue'
import ContextMenu from './ContextMenu.vue'
import { NODE_CATEGORIES, MASTERY_THRESHOLDS } from '@/utils/constants'
import { useAppStore } from '@/stores/app'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const knowledgeStore = useKnowledgeStore()

const { onNodeClick, onPaneClick, onNodeContextMenu, fitView } = useVueFlow()
const appStore = useAppStore()

const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const contextMenu = ref<{ visible: boolean; x: number; y: number; nodeId: string | null }>({
  visible: false,
  x: 0,
  y: 0,
  nodeId: null
})

// MiniMap 节点颜色：根据掌握度着色
const miniMapNodeColor: MiniMapNodeFunc = (node) => {
  const mastery = node.data?.mastery ?? 0
  if (mastery >= MASTERY_THRESHOLDS.excellent) return '#34c759'
  if (mastery >= MASTERY_THRESHOLDS.good) return '#007aff'
  if (mastery >= MASTERY_THRESHOLDS.weak) return '#ff9500'
  return '#e5e5ea'
}

// 搜索和筛选
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedMastery = ref('')

// 计算过滤后的节点
const filteredNodes = computed(() => {
  let filtered = knowledgeStore.nodes
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(node => 
      node.name.toLowerCase().includes(query) || 
      node.description.toLowerCase().includes(query)
    )
  }
  
  if (selectedCategory.value) {
    filtered = filtered.filter(node => node.category === selectedCategory.value)
  }
  
  if (selectedMastery.value) {
    const mastery = selectedMastery.value
    filtered = filtered.filter(node => {
      const nodeMastery = knowledgeStore.getNodeMastery(node.id)
      if (mastery === 'excellent') return nodeMastery >= 90
      if (mastery === 'good') return nodeMastery >= 60 && nodeMastery < 90
      if (mastery === 'weak') return nodeMastery < 60
      return true
    })
  }
  
  return filtered
})

// 初始化节点和边
const initGraph = () => {
  updateGraph()
}

// 更新图谱
const updateGraph = () => {
  const knowledgeNodes = filteredNodes.value
  const knowledgeEdges = knowledgeStore.edges

  // 创建VueFlow节点
  nodes.value = knowledgeNodes.map((node, index) => ({
    id: node.id,
    type: 'custom',
    position: { 
      x: Math.cos(index / knowledgeNodes.length * Math.PI * 2) * 300 + 400,
      y: Math.sin(index / knowledgeNodes.length * Math.PI * 2) * 300 + 300
    },
    data: {
      label: node.name,
      description: node.description,
      category: node.category,
      importance: node.importance,
      mastery: knowledgeStore.getNodeMastery(node.id)
    }
  }))

  // 创建VueFlow边（只包含过滤后的节点之间的边）
  const filteredNodeIds = new Set(knowledgeNodes.map(n => n.id))
  edges.value = knowledgeEdges
    .filter(edge => filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target))
    .map(edge => ({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'custom',
      animated: edge.relationType === 'prerequisite',
      data: {
        relationType: edge.relationType,
        strength: edge.strength
      }
    }))
}

// 处理节点点击
onNodeClick(({ node }) => {
  const targetNode = knowledgeStore.getNodeById(node.id) || null
  knowledgeStore.selectNode(targetNode)
  if (targetNode) {
    appStore.openPanel(targetNode.id)
  }
})

// 处理空白区域点击
onPaneClick(() => {
  knowledgeStore.selectNode(null)
  contextMenu.value.visible = false
})

// 处理节点右键菜单
onNodeContextMenu(({ event, node }) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: (event as MouseEvent).clientX,
    y: (event as MouseEvent).clientY,
    nodeId: node.id
  }
})

// 关闭上下文菜单
const closeContextMenu = () => {
  contextMenu.value.visible = false
}

// 处理上下文菜单操作
const handleContextMenuAction = (action: string, nodeId: string) => {
  closeContextMenu()
  
  switch (action) {
    case 'explain':
      appStore.openAgentWithAction('explain', nodeId)
      break
    case 'practice':
      appStore.openAgentWithAction('practice', nodeId)
      break
    case 'plan':
      appStore.openAgentWithAction('plan', nodeId)
      break
    case 'errors':
      // mock for now
      break
  }
}

// 清除筛选
const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedMastery.value = ''
}

// 监听筛选变化
watch([searchQuery, selectedCategory, selectedMastery], () => {
  updateGraph()
})

// 监听选中节点变化以更新视图
watch(() => appStore.panelNodeId, (newNodeId) => {
  if (newNodeId) {
    const node = knowledgeStore.getNodeById(newNodeId)
    if (node) {
      knowledgeStore.selectNode(node)
      fitView({ nodes: [newNodeId], duration: 500 })
    }
  }
})

onMounted(() => {
  initGraph()
  
  // 如果有初始节点，聚焦到该节点
  const nodeId = appStore.panelNodeId
  if (nodeId) {
    setTimeout(() => {
      fitView({ nodes: [nodeId], duration: 500 })
    }, 100)
  }
})
</script>

<template>
  <div class="w-full h-full relative">
    <!-- 搜索和筛选工具栏 -->
    <div class="map-toolbar">
      <div class="search-wrapper">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索知识点..."
          class="map-search-input"
        />
      </div>

      <select v-model="selectedCategory" class="map-select">
        <option value="">所有分类</option>
        <option v-for="category in NODE_CATEGORIES" :key="category" :value="category">{{ category }}</option>
      </select>

      <select v-model="selectedMastery" class="map-select">
        <option value="">所有掌握度</option>
        <option value="excellent">已掌握 (≥90%)</option>
        <option value="good">学习中 (60-90%)</option>
        <option value="weak">薄弱 (&lt;60%)</option>
      </select>

      <button v-if="searchQuery || selectedCategory || selectedMastery" @click="clearFilters" class="clear-filter-btn">
        ✕ 清除
      </button>
    </div>

    <!-- 节点统计 -->
    <div class="map-stats">
      <span class="stats-text">{{ filteredNodes.length }} / {{ knowledgeStore.nodes.length }} 个知识点</span>
    </div>

    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :default-viewport="{ zoom: 0.8, x: 0, y: 0 }"
      :min-zoom="0.2"
      :max-zoom="4"
      class="w-full h-full"
    >
      <!-- 自定义节点模板 -->
      <template #node-custom="nodeProps">
        <MapNode v-bind="nodeProps" />
      </template>

      <!-- 自定义边模板 -->
      <template #edge-custom="edgeProps">
        <MapEdge v-bind="edgeProps" />
      </template>

      <!-- 背景 -->
      <Background :gap="20" :size="1" />

      <!-- 控制器 -->
      <Controls />

      <!-- 小地图 -->
      <MiniMap
        :node-color="miniMapNodeColor"
        :node-stroke-width="2"
        :width="180"
        :height="140"
        :mask-color="'rgba(0, 0, 0, 0.06)'"
        :pannable="true"
        :zoomable="true"
        class="custom-minimap"
      />
    </VueFlow>

    <!-- 底部图例 -->
    <div class="minimap-legend">
      <div class="legend-item">
        <span class="legend-dot" style="background: #34c759"></span>
        已掌握
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background: #007aff"></span>
        学习中
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background: #ff9500"></span>
        薄弱
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background: #e5e5ea"></span>
        未学习
      </div>
    </div>

    <!-- 右键菜单 -->
    <ContextMenu
      v-if="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      :node-id="contextMenu.nodeId"
      @close="closeContextMenu"
      @action="handleContextMenuAction"
    />
  </div>
</template>

<style scoped>
/* Map toolbar - centered top floating capsule */
.map-toolbar {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-md);
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-tertiary);
  pointer-events: none;
  z-index: 1;
}

.map-search-input {
  width: 220px;
  padding: 8px 12px 8px 32px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  backdrop-filter: blur(12px);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.map-search-input:focus {
  border-color: var(--info);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12);
}

.map-search-input::placeholder { color: var(--text-tertiary); }

.map-select {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
  backdrop-filter: blur(12px);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.map-select:focus {
  border-color: var(--info);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12);
}

.clear-filter-btn {
  padding: 8px 12px;
  background: rgba(255, 59, 48, 0.08);
  border: 1px solid rgba(255, 59, 48, 0.25);
  border-radius: var(--radius-md);
  color: var(--danger);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filter-btn:hover {
  background: rgba(255, 59, 48, 0.18);
}

/* Stats */
.map-stats {
  position: absolute;
  top: 16px;
  right: 150px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 6px 14px;
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-sm);
}

.stats-text {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* MiniMap 玻璃态优化 */
:deep(.vue-flow__minimap) {
  background: rgba(255, 255, 255, 0.78) !important;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-lg) !important;
  overflow: hidden;
}

:deep(.vue-flow__minimap-mask) {
  fill: rgba(0, 0, 0, 0.05);
  rx: 8;
  ry: 8;
}

:deep(.vue-flow__minimap-node) {
  stroke-width: 1.5;
  rx: 3;
  ry: 3;
}

/* 底部图例 */
.minimap-legend {
  position: absolute;
  bottom: 20px;
  right: 210px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>