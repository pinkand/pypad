import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import type { KnowledgeNode, KnowledgeEdge, KnowledgeCluster, GraphResponse } from '@/types/knowledge'
import { saveToStorage, loadFromStorage, STORAGE_KEYS } from '@/utils/storage'
import { knowledgeApi } from '@/services/api'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const nodes = ref<KnowledgeNode[]>([])
  const treeNodes = ref<KnowledgeNode[]>([]) // Root nodes of the tree
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
      
      // 从API或本地JSON加载数据
      const response = await fetch('/data/python-knowledge.json')
      const data = await response.json()
      
      const rawNodes: KnowledgeNode[] = data.nodes || []
      const rawEdges: KnowledgeEdge[] = data.edges || []
      
      edges.value = rawEdges
      clusters.value = data.clusters || []
      
      // 构建自定义架构的树状结构
      const coreNode: KnowledgeNode = {
        id: 'python-core',
        name: 'Python核心',
        description: 'Python编程语言核心知识体系',
        category: 'Root',
        importance: 10,
        prerequisites: [],
        children: []
      }
      
      const domainNodes: Record<string, KnowledgeNode> = {
        'basic-syntax': { id: 'basic-syntax', name: '基础语法', description: '变量、数据类型、控制流等', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core' },
        'data-structures': { id: 'data-structures', name: '数据结构', description: '列表、字典、集合等数据结构', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core' },
        'oop': { id: 'oop', name: '面向对象', description: '类、对象、继承、多态', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core' },
        'web-dev': { id: 'web-dev', name: 'Web开发', description: '网络编程、Web框架及数据库', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core' },
        'data-analysis': { id: 'data-analysis', name: '数据分析', description: '数据处理与分析', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core' },
        'ai-dev': { id: 'ai-dev', name: 'AI开发', description: '人工智能、机器学习', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core' },
      }
      
      coreNode.children = Object.values(domainNodes)

      const nodeMap = new Map<string, KnowledgeNode>()
      nodeMap.set(coreNode.id, coreNode)
      Object.values(domainNodes).forEach(d => nodeMap.set(d.id, d))
      
      rawNodes.forEach(n => {
        n.children = []
        
        // 按照领域映射分类
        let domainId = 'basic-syntax'
        if (['基础语法', '控制流', '函数', '异常处理'].includes(n.category)) domainId = 'basic-syntax'
        else if (['数据类型', '文件IO', '迭代器与生成器'].includes(n.category)) domainId = 'data-structures'
        else if (['面向对象'].includes(n.category)) domainId = 'oop'
        else if (['Web框架', '网络编程', '数据库', '异步编程'].includes(n.category)) domainId = 'web-dev'
        else if (['数据分析', '测试', '性能优化', '模块与包'].includes(n.category)) domainId = 'data-analysis'
        else if (['AI开发'].includes(n.category)) domainId = 'ai-dev'
        else if (['装饰器'].includes(n.category)) domainId = 'oop'
        
        n.parentId = domainId
        const domainNode = domainNodes[domainId]
        if (domainNode && domainNode.children) {
          domainNode.children.push(n)
        }
        nodeMap.set(n.id, n)
      })
      
      treeNodes.value = [coreNode]
      nodes.value = [coreNode, ...Object.values(domainNodes), ...rawNodes]
      
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
    treeNodes,
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