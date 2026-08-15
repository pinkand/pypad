import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import type { KnowledgeNode, KnowledgeEdge, KnowledgeCluster } from '@/types/knowledge'
import { saveToStorage, loadFromStorage, STORAGE_KEYS } from '@/utils/storage'
import { knowledgeApi, userApi } from '@/services/api'
import { useUserStore } from './user'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const nodes = ref<KnowledgeNode[]>([])
  const treeNodes = ref<KnowledgeNode[]>([])
  const edges = ref<KnowledgeEdge[]>([])
  const clusters = ref<KnowledgeCluster[]>([])
  const selectedNode = ref<KnowledgeNode | null>(null)
  const masteryMap = ref<Map<string, number>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 加载掌握度 — 优先从后端 API 拉取，fallback 到 localStorage
  const loadMasteryFromStorage = async () => {
    try {
      const userStore = useUserStore()
      const userId = userStore.authUser?.id || 'user-1'
      const res: any = await userApi.getKnowledge(userId)
      const backendKnowledge: Record<string, number> = res?.knowledge || {}
      if (Object.keys(backendKnowledge).length > 0) {
        const map = new Map<string, number>()
        Object.entries(backendKnowledge).forEach(([key, value]) => {
          map.set(key, value as number)
        })
        masteryMap.value = map
        // 同步到 localStorage 作为离线缓存
        saveMasteryToStorage()
        return
      }
    } catch {
      // API 失败则 fallback 到 localStorage
    }
    const savedMastery = loadFromStorage<Record<string, number>>(STORAGE_KEYS.KNOWLEDGE_MASTERY, {})
    const map = new Map<string, number>()
    Object.entries(savedMastery).forEach(([key, value]) => {
      map.set(key, value)
    })
    masteryMap.value = map
  }

  // 保存掌握度到 localStorage（离线缓存）
  const saveMasteryToStorage = () => {
    const obj: Record<string, number> = {}
    masteryMap.value.forEach((value, key) => {
      obj[key] = value
    })
    saveToStorage(STORAGE_KEYS.KNOWLEDGE_MASTERY, obj)
  }

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

  // ----------------------------------------------------
  // Adapter 适配器：转换为 Three.js (KnowledgeUniverse) 结构
  // ----------------------------------------------------
  const threeTreeData = computed(() => {
    return treeNodes.value
  })

  // ----------------------------------------------------
  // Adapter 适配器：转换为 VueFlow (KnowledgeMap) 结构
  // ----------------------------------------------------
  const vueFlowGraphData = computed(() => {
    const vfNodes = nodes.value.map((node, index) => ({
      id: node.id,
      label: node.name,
      type: 'knowledgeNode',
      position: node.position || { x: (index % 5) * 200, y: Math.floor(index / 5) * 120 },
      data: {
        category: node.category,
        importance: node.importance,
        mastery: masteryMap.value.get(node.id) || 0
      }
    }))

    const vfEdges = edges.value.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      animated: edge.relationType === 'prerequisite',
      style: { stroke: edge.strength === 'hard' ? '#f43f5e' : '#3b82f6' }
    }))

    return { nodes: vfNodes, edges: vfEdges }
  })

  const getNodeById = (id: string) => {
    return nodes.value.find(node => node.id === id)
  }

  const getNodeMastery = (nodeId: string) => {
    return masteryMap.value.get(nodeId) || 0
  }

  const setNodeMastery = async (nodeId: string, mastery: number) => {
    const clampedMastery = Math.max(0, Math.min(100, mastery))
    masteryMap.value.set(nodeId, clampedMastery)
    const node = getNodeById(nodeId)
    if (node) {
      node.masteryScore = clampedMastery
      node.mastery = {
        score: clampedMastery,
        status: clampedMastery >= 90 ? 'mastered' : clampedMastery >= 60 ? 'learning' : clampedMastery > 0 ? 'weak' : 'unlearned'
      }
    }
    // 同步到后端
    try {
      const userStore = useUserStore()
      const userId = userStore.authUser?.id || 'user-1'
      await userApi.updateKnowledge({ userId, knowledgeId: nodeId, masteryScore: clampedMastery })
    } catch {
      // 静默失败，localStorage 已保存
    }
  }

  const selectNode = (node: KnowledgeNode | null) => {
    selectedNode.value = node
  }

  const loadData = async () => {
    loading.value = true
    error.value = null

    try {
      await loadMasteryFromStorage()

      // Fetch from backend API (replaces static JSON)
      const [nodesResp, edgesResp] = await Promise.all([
        knowledgeApi.getNodes(),
        knowledgeApi.getRelations(),
      ])
      const rawNodes: any[] = Array.isArray(nodesResp) ? nodesResp : (nodesResp as any).data || []
      const rawEdges: any[] = Array.isArray(edgesResp) ? edgesResp : (edgesResp as any).data || []

      // Build prerequisites map from edges
      const prereqMap = new Map<string, string[]>()
      rawEdges.forEach((e: any) => {
        const target = e.target || e.target_id
        const source = e.source || e.source_id
        if (!prereqMap.has(target)) prereqMap.set(target, [])
        prereqMap.get(target)!.push(source)
      })

      // Adapt API node format → frontend KnowledgeNode
      const apiNodes: KnowledgeNode[] = (rawNodes || []).map((n: any) => ({
        id: n.id,
        code: n.code,
        name: n.name,
        description: n.description || '',
        category: n.category || '',
        importance: n.importance || 5,
        prerequisites: prereqMap.get(n.id) || [],
        courseId: n.courseId || 'py-course-1',
        chapterId: n.chapterId,
        sectionId: n.sectionId,
        aiSummary: n.aiSummary || {
          overview: `${n.name}核心原理与使用指南`,
          keyPoints: ['语法规范', '最佳实践', '常见坑点'],
          commonPitfalls: ['类型错误', '作用域混淆'],
        },
        position: n.position || undefined,
        parentId: n.parentId || n.parent_id,
        depth: n.depth,
        sortOrder: n.sortOrder || n.sort_order,
        masteryScore: masteryMap.value.get(n.id) || 0,
        mastery: {
          score: masteryMap.value.get(n.id) || 0,
          status: (masteryMap.value.get(n.id) || 0) >= 90 ? 'mastered'
            : (masteryMap.value.get(n.id) || 0) >= 60 ? 'learning'
            : (masteryMap.value.get(n.id) || 0) > 0 ? 'weak' : 'unlearned',
        },
      }))

      // Adapt API edge format → frontend KnowledgeEdge
      const apiEdges: KnowledgeEdge[] = (rawEdges || []).map((e: any) => ({
        id: e.id || `${e.source || e.source_id}-${e.target || e.target_id}`,
        source: e.source || e.source_id,
        target: e.target || e.target_id,
        relationType: e.relationType || e.relation_type || 'prerequisite',
        strength: e.strength || 'soft',
        weight: e.weight,
      }))

      edges.value = apiEdges

      // Build virtual domain / root nodes for tree structure
      const coreNode: KnowledgeNode = {
        id: 'python-core', code: 'PY-CORE', name: 'Python核心',
        description: 'Python编程语言核心知识体系', category: 'Root',
        importance: 10, prerequisites: [], children: [], courseId: 'py-course-1',
      }

      const domainNodes: Record<string, KnowledgeNode> = {
        'env': { id: 'env', name: '基础环境', description: '开发环境搭建与编程规范', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-1' },
        'syntax': { id: 'syntax', name: '基本语法', description: '输入输出、变量与运算符', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-2' },
        'control': { id: 'control', name: '控制结构', description: '条件分支与循环结构', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-3' },
        'ds': { id: 'ds', name: '数据结构', description: '字符串、列表、元组、字典与集合', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-4' },
        'func': { id: 'func', name: '函数设计', description: '函数定义、参数传递与作用域', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-6' },
        'module': { id: 'module', name: '模块与架构', description: '模块、标准库与第三方包', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-8' },
        'oop': { id: 'oop', name: '面向对象', description: '类、对象、封装与继承', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-9' },
        'file': { id: 'file', name: '文件与数据', description: '文件 I/O 与持久化存储', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-10' },
        'robust': { id: 'robust', name: '程序健壮性', description: '异常处理与调试断言', category: 'Domain', importance: 9, prerequisites: ['python-core'], children: [], parentId: 'python-core', courseId: 'py-course-1', chapterId: 'chap-11' },
      }

      coreNode.children = Object.values(domainNodes)

      // Categorize each API node into a domain
      apiNodes.forEach(n => {
        n.children = []
        let domainId = 'syntax'
        if (n.category === '基础环境') domainId = 'env'
        else if (n.category === '基本语法') domainId = 'syntax'
        else if (n.category === '控制结构') domainId = 'control'
        else if (n.category === '数据结构') domainId = 'ds'
        else if (n.category === '函数设计') domainId = 'func'
        else if (n.category === '模块与架构') domainId = 'module'
        else if (n.category === '面向对象') domainId = 'oop'
        else if (n.category === '文件与数据') domainId = 'file'
        else if (n.category === '健壮性') domainId = 'robust'

        n.parentId = domainId
        const domainNode = domainNodes[domainId]
        if (domainNode && domainNode.children) {
          domainNode.children.push(n)
        }
      })

      treeNodes.value = [coreNode]
      nodes.value = [coreNode, ...Object.values(domainNodes), ...apiNodes]

      nodes.value.forEach(node => {
        if (!masteryMap.value.has(node.id)) {
          masteryMap.value.set(node.id, 0)
        }
      })
    } catch (err) {
      error.value = '加载知识数据失败，请确保后端服务已启动'
      console.error('Failed to load knowledge data from API:', err)
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
    threeTreeData,
    vueFlowGraphData,
    getNodeById,
    getNodeMastery,
    setNodeMastery,
    selectNode,
    loadData
  }
})