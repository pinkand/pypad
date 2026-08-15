import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Practice } from '@/types/knowledge'
import { practiceApi } from '@/services/api'

export const usePracticeStore = defineStore('practice', () => {
  const practices = ref<Practice[]>([])
  const currentPractice = ref<Practice | null>(null)
  const loading = ref(false)

  const fetchPracticesByNode = async (knowledgeId: string) => {
    loading.value = true
    try {
      const res = await practiceApi.getPracticesByNode(knowledgeId)
      practices.value = (res as any).practices || res || []
    } catch (err) {
      practices.value = []
    } finally {
      loading.value = false
    }
  }

  const generateAIPractice = async (knowledgeId: string, difficulty: string = 'medium') => {
    loading.value = true
    try {
      const res = await practiceApi.generateAIPractice(knowledgeId, difficulty)
      const newPractice = (res as any).practice || res
      practices.value.push(newPractice)
      currentPractice.value = newPractice
      return newPractice
    } finally {
      loading.value = false
    }
  }

  const submitPractice = async (practiceId: string, code: string) => {
    return await practiceApi.submitPractice(practiceId, code)
  }

  return {
    practices,
    currentPractice,
    loading,
    fetchPracticesByNode,
    generateAIPractice,
    submitPractice
  }
})
