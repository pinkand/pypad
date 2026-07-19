import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserProfile, UserStats, LearningPath, StudyRecord, WrongQuestion } from '@/types/knowledge'

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
  const learningPaths = ref<LearningPath[]>([])
  const currentPath = ref<LearningPath | null>(null)
  const studyRecords = ref<StudyRecord[]>([])
  const wrongQuestions = ref<WrongQuestion[]>([])

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

  // 方法
  const loadProfile = async () => {
    try {
      // 模拟数据
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
    } catch (err) {
      console.error('Failed to load user profile:', err)
    }
  }

  const addStudyRecord = (record: Omit<StudyRecord, 'id' | 'createdAt'>) => {
    studyRecords.value.push({
      ...record,
      id: Date.now().toString(),
      createdAt: new Date().toISOString()
    })
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

  return {
    profile,
    stats,
    learningPaths,
    currentPath,
    studyRecords,
    wrongQuestions,
    masteryPercentage,
    recentStudyRecords,
    unresolvedWrongQuestions,
    loadProfile,
    addStudyRecord,
    addWrongQuestion,
    resolveWrongQuestion,
    updateStats
  }
})