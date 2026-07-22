<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Node, Edge } from '@vue-flow/core'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { useKnowledgeStore } from '@/stores/knowledge'
import MapNode from './MapNode.vue'
import MapEdge from './MapEdge.vue'
import ContextMenu from './ContextMenu.vue'
import { NODE_CATEGORIES } from '@/utils/constants'
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
      <MiniMap />
    </VueFlow>

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
/* Map toolbar */
.map-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: #475569;
  pointer-events: none;
  z-index: 1;
}

.map-search-input {
  width: 220px;
  padding: 8px 12px 8px 32px;
  background: rgba(10, 22, 40, 0.88);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 13px;
  outline: none;
  backdrop-filter: blur(12px);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.map-search-input:focus {
  border-color: rgba(99, 102, 241, 0.55);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.map-search-input::placeholder { color: #334155; }

.map-select {
  padding: 8px 10px;
  background: rgba(10, 22, 40, 0.88);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 8px;
  color: #94a3b8;
  font-size: 12px;
  outline: none;
  backdrop-filter: blur(12px);
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.map-select:focus {
  border-color: rgba(99, 102, 241, 0.55);
}

.clear-filter-btn {
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #f87171;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filter-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* Stats */
.map-stats {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  background: rgba(10, 22, 40, 0.88);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 8px;
  padding: 6px 14px;
  backdrop-filter: blur(12px);
}

.stats-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}
</style>