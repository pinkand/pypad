import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserProfile, UserStats, LearningPath, StudyRecord, WrongQuestion } from '@/types/knowledge'
import { authApi, userApi, dashboardApi, analyticsApi } from '@/services/api'
import { loadFromStorage, saveToStorage, STORAGE_KEYS } from '@/utils/storage'

export interface AIConfig {
  provider: 'openai' | 'deepseek' | 'ollama' | 'mock'
  apiKey: string
  baseUrl: string
  model: string
  temperature: number
  maxTokens: number
}

const DEFAULT_AI_CONFIG: AIConfig = {
  provider: 'mock',
  apiKey: '',
  baseUrl: 'https://api.deepseek.com',
  model: 'deepseek-chat',
  temperature: 0.7,
  maxTokens: 1000
}

export const useUserStore = defineStore('user', () => {
  const profile = ref<UserProfile | null>(null)
  const stats = ref<UserStats>({
    totalNodes: 0,
    masteredNodes: 0,
    learningNodes: 0,
    weakNodes: 0,
    totalTimeSpent: 0,
    averageMastery: 0
  })

  // 全局 AI 配置状态（优先从 localStorage 恢复）
  const savedAiConfig = loadFromStorage<AIConfig>(STORAGE_KEYS.AI_CONFIG, DEFAULT_AI_CONFIG)
  const aiConfig = ref<AIConfig>({ ...DEFAULT_AI_CONFIG, ...savedAiConfig })

  const saveAiConfig = (newConfig: Partial<AIConfig>) => {
    aiConfig.value = { ...aiConfig.value, ...newConfig }
    saveToStorage(STORAGE_KEYS.AI_CONFIG, aiConfig.value)
  }

  const updateProfile = (data: Partial<UserProfile>) => {
    if (profile.value) {
      profile.value = { ...profile.value, ...data }
    } else {
      profile.value = {
        id: authUser.value?.id || 'user-1',
        name: data.name || '学习者',
        email: data.email || 'user@example.com',
        currentGoal: data.currentGoal || 'Python后端开发',
        level: 1,
        experience: 0,
        streak: 0,
        createdAt: new Date().toISOString()
      }
    }
  }
  const learningPaths = ref<LearningPath[]>([])
  const currentPath = ref<LearningPath | null>(null)
  const studyRecords = ref<StudyRecord[]>([])
  const wrongQuestions = ref<WrongQuestion[]>([])
  const authUser = ref<any>(null)
  const authLoading = ref(false)

  const isLoggedIn = computed(() => !!authUser.value)

  // 计算属性
  const masteryPercentage = computed(() => {
    if (stats.value.totalNodes === 0) return 0
    return Math.round((stats.value.masteredNodes / stats.value.totalNodes) * 100)
  })

  const recentStudyRecords = computed(() => {
    return [...studyRecords.value]
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 10)
  })

  const unresolvedWrongQuestions = computed(() => {
    return wrongQuestions.value.filter(q => !q.resolved)
  })

  // ── Auth methods ──────────────────────────────
  const login = async (username: string, password: string) => {
    authLoading.value = true
    try {
      const res: any = await authApi.login({ username, password })
      localStorage.setItem('auth_token', res.token)
      authUser.value = res.user
      return res.user
    } finally {
      authLoading.value = false
    }
  }

  const register = async (username: string, email: string, password: string, displayName?: string) => {
    authLoading.value = true
    try {
      const res: any = await authApi.register({ username, email, password, displayName })
      localStorage.setItem('auth_token', res.token)
      authUser.value = res.user
      return res.user
    } finally {
      authLoading.value = false
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    authUser.value = null
  }

  const restoreSession = async () => {
    const token = localStorage.getItem('auth_token')
    if (!token) return
    try {
      const res: any = await authApi.me()
      authUser.value = res
    } catch {
      localStorage.removeItem('auth_token')
    }
  }

  // ── Profile methods ───────────────────────────
  const loadProfile = async () => {
    try {
      if (authUser.value) {
        profile.value = {
          id: authUser.value.id,
          name: authUser.value.displayName || authUser.value.username,
          email: authUser.value.email,
          currentGoal: 'Python后端开发',
          level: authUser.value.level || 1,
          experience: authUser.value.experience || 0,
          streak: authUser.value.streak || 0,
          createdAt: new Date().toISOString()
        }
      } else {
        profile.value = {
          id: 'user-1',
          name: '学习者',
          email: 'learner@example.com',
          currentGoal: 'Python后端开发',
          level: 1,
          experience: 0,
          streak: 0,
          createdAt: new Date().toISOString()
        }
      }
    } catch (err) {
      console.error('Failed to load user profile:', err)
    }
  }

  const addStudyRecord = async (record: Omit<StudyRecord, 'id' | 'createdAt'>) => {
    studyRecords.value.push({
      ...record,
      id: Date.now().toString(),
      createdAt: new Date().toISOString()
    })
    // 同步到后端
    try {
      await userApi.recordStudy({
        userId: authUser.value?.id || 'user-1',
        knowledgeId: record.knowledgeNodeId,
        duration: record.duration,
        behavior: record.behavior,
      })
    } catch {
      // 静默失败，本地数据已保存
    }
  }

  const addWrongQuestion = (question: Omit<WrongQuestion, 'id' | 'createdAt' | 'resolved'>) => {
    wrongQuestions.value.push({
      ...question,
      id: Date.now().toString(),
      resolved: false,
      createdAt: new Date().toISOString()
    })
  }

  const resolveWrongQuestion = (id: string) => {
    const question = wrongQuestions.value.find(q => q.id === id)
    if (question) {
      question.resolved = true
    }
  }

  const updateStats = (newStats: Partial<UserStats>) => {
    stats.value = { ...stats.value, ...newStats }
  }

  // 从后端加载 Dashboard 统计数据
  const loadDashboardStats = async () => {
    try {
      const [overviewRes, analyticsRes]: any[] = await Promise.all([
        dashboardApi.getOverview(authUser.value?.id),
        analyticsApi.getOverview(authUser.value?.id),
      ])
      if (overviewRes) {
        stats.value = {
          totalNodes: analyticsRes?.totalNodes || stats.value.totalNodes,
          masteredNodes: analyticsRes?.masteredNodes || stats.value.masteredNodes,
          learningNodes: ((analyticsRes?.totalNodes || 0) - (analyticsRes?.masteredNodes || 0)) || stats.value.learningNodes,
          weakNodes: (overviewRes.weakKnowledgeNodeIds?.length) || stats.value.weakNodes,
          totalTimeSpent: overviewRes.totalStudyTimeSeconds || stats.value.totalTimeSpent,
          averageMastery: analyticsRes?.averageMastery || stats.value.averageMastery,
        }
      }
    } catch {
      // 保留本地数据
    }
  }

  // 从后端加载学习记录
  const loadStudyRecords = async () => {
    try {
      const res: any = await userApi.getStudyRecords(authUser.value?.id)
      const records = res?.records || []
      studyRecords.value = records.map((r: any) => ({
        id: r.id?.toString() || Date.now().toString(),
        userId: r.userId,
        knowledgeNodeId: r.knowledgeNodeId,
        duration: r.duration,
        behavior: r.behavior,
        createdAt: r.createdAt,
      }))
    } catch {
      // 保留本地数据
    }
  }

  return {
    profile,
    stats,
    learningPaths,
    currentPath,
    studyRecords,
    wrongQuestions,
    authUser,
    authLoading,
    isLoggedIn,
    masteryPercentage,
    recentStudyRecords,
    unresolvedWrongQuestions,
    aiConfig,
    saveAiConfig,
    updateProfile,
    login,
    register,
    logout,
    restoreSession,
    loadProfile,
    addStudyRecord,
    addWrongQuestion,
    resolveWrongQuestion,
    updateStats,
    loadDashboardStats,
    loadStudyRecords
  }
})
