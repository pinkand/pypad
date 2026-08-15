import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Session, SessionEventLog, SessionEventType } from '@/types/knowledge'
import { sessionApi } from '@/services/api'
import { useUserStore } from './user'

export const useSessionStore = defineStore('session', () => {
  const currentSession = ref<Session | null>(null)
  const eventLogs = ref<SessionEventLog[]>([])
  const isSessionActive = computed(() => currentSession.value?.status === 'active')

  const startSession = async (knowledgeNodeId: string, courseId?: string, chapterId?: string, sectionId?: string) => {
    try {
      const userStore = useUserStore()
      const userId = userStore.authUser?.id || 'user-1'
      const res = await sessionApi.startSession({
        userId,
        knowledgeNodeId,
        courseId,
        chapterId,
        sectionId
      })
      currentSession.value = (res as any).session || res || {
        id: `sess-${Date.now()}`,
        userId: 'user-1',
        knowledgeNodeId,
        status: 'active',
        startTime: new Date().toISOString(),
        totalDurationSeconds: 0,
        eventLogs: [],
        workspaceRuns: [],
        reviews: []
      }
      eventLogs.value = []
      await recordEvent('open_node', { knowledgeNodeId })
    } catch (err) {
      console.error('Failed to start session:', err)
    }
  }

  const recordEvent = async (eventType: SessionEventType, payload: Record<string, unknown> = {}) => {
    if (!currentSession.value) return
    const log: SessionEventLog = {
      id: `evt-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      sessionId: currentSession.value.id,
      eventType,
      payload,
      timestamp: new Date().toISOString()
    }
    eventLogs.value.push(log)
    try {
      await sessionApi.recordEvent(currentSession.value.id, eventType, payload)
    } catch (err) {
      // 静默缓存
    }
  }

  const endSession = async () => {
    if (!currentSession.value) return
    try {
      await recordEvent('close_session', {})
      await sessionApi.endSession(currentSession.value.id)
      if (currentSession.value) {
        currentSession.value.status = 'completed'
        currentSession.value.endTime = new Date().toISOString()
      }
    } finally {
      currentSession.value = null
    }
  }

  return {
    currentSession,
    eventLogs,
    isSessionActive,
    startSession,
    recordEvent,
    endSession
  }
})
