import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import type { KnowledgeNode, KnowledgeEdge, KnowledgeCluster } from '@/types/knowledge'
import { saveToStorage, loadFromStorage, STORAGE_KEYS } from '@/utils/storage'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const nodes = ref<KnowledgeNode[]>([])
  const edges = ref<KnowledgeEdge[]>([])
  const clusters = ref<KnowledgeCluster[]>([])
  const selectedNode = ref<KnowledgeNode | null>(null)
  const masteryMap = ref<Map<string, number>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 从localStorage加载掌握度数据
  const loadMasteryFromStorage = () => {
    const savedMastery = loadFromStorage<Record<string, number>>(STORAGE_KEYS.KNOWLEDGE_MASTERY, {})
    const map = new Map<string, number>()
    Object.entries(savedMastery).forEach(([key, value]) => {
      map.set(key, value)
    })
    masteryMap.value = map
  }

  // 保存掌握度数据到localStorage
  const saveMasteryToStorage = () => {
    const obj: Record<string, number> = {}
    masteryMap.value.forEach((value, key) => {
      obj[key] = value
    })
    saveToStorage(STORAGE_KEYS.KNOWLEDGE_MASTERY, obj)
  }

  // 监听掌握度变化，自动保存
  watch(masteryMap, () => {
    saveMasteryToStorage()
  }, { deep: true })

  // 计算属性
  const nodesByCategory = computed(() => {
    const map = new Map<string, KnowledgeNode[]>()
    nodes.value.forEach(node => {
      const category = node.category
      if (!map.has(category)) {
        map.set(category, [])
      }
      map.get(category)!.push(node)
    })
    return map
  })

  const weakNodes = computed(() => {
    return nodes.value.filter(node => {
      const mastery = masteryMap.value.get(node.id) || 0
      return mastery < 60
    })
  })

  const strongNodes = computed(() => {
    return nodes.value.filter(node => {
      const mastery = masteryMap.value.get(node.id) || 0
      return mastery >= 90
    })
  })

  const getNodeById = (id: string) => {
    return nodes.value.find(node => node.id === id)
  }

  const getNodeMastery = (nodeId: string) => {
    return masteryMap.value.get(nodeId) || 0
  }

  const setNodeMastery = (nodeId: string, mastery: number) => {
    masteryMap.value.set(nodeId, Math.max(0, Math.min(100, mastery)))
  }

  const selectNode = (node: KnowledgeNode | null) => {
    selectedNode.value = node
  }

  const loadData = async () => {
    loading.value = true
    error.value = null
    
    try {
      // 从localStorage加载掌握度数据
      loadMasteryFromStorage()
      
      // 这里从API或本地JSON加载数据
      const response = await fetch('/data/python-knowledge.json')
      const data = await response.json()
      
      nodes.value = data.nodes || []
      edges.value = data.edges || []
      clusters.value = data.clusters || []
      
      // 初始化掌握度（如果不存在）
      nodes.value.forEach(node => {
        if (!masteryMap.value.has(node.id)) {
          masteryMap.value.set(node.id, 0)
        }
      })
    } catch (err) {
      error.value = '加载知识数据失败'
      console.error('Failed to load knowledge data:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    nodes,
    edges,
    clusters,
    selectedNode,
    masteryMap,
    loading,
    error,
    nodesByCategory,
    weakNodes,
    strongNodes,
    getNodeById,
    getNodeMastery,
    setNodeMastery,
    selectNode,
    loadData
  }
})