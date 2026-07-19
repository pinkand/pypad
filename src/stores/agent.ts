import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Message, Task, Recommendation, AgentType } from '@/types/agent'

export const useAgentStore = defineStore('agent', () => {
  const messages = ref<Message[]>([])
  const currentAgent = ref<AgentType>('tutor')
  const tasks = ref<Task[]>([])
  const recommendations = ref<Recommendation[]>([])
  const isTyping = ref(false)
  const activeTask = ref<Task | null>(null)

  // 计算属性
  const recentMessages = computed(() => {
    return [...messages.value]
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .slice(-50)
  })

  const pendingTasks = computed(() => {
    return tasks.value.filter(t => t.status === 'pending')
  })

  const inProgressTasks = computed(() => {
    return tasks.value.filter(t => t.status === 'in_progress')
  })

  const completedTasks = computed(() => {
    return tasks.value.filter(t => t.status === 'completed')
  })

  const highPriorityRecommendations = computed(() => {
    return recommendations.value
      .filter(r => r.priority >= 8)
      .sort((a, b) => b.priority - a.priority)
  })

  // 方法
  const addMessage = (role: 'user' | 'assistant' | 'system', content: string, agentType?: AgentType) => {
    messages.value.push({
      id: Date.now().toString(),
      role,
      content,
      agentType: agentType || currentAgent.value,
      timestamp: new Date().toISOString()
    })
  }

  const setAgent = (agent: AgentType) => {
    currentAgent.value = agent
  }

  const addTask = (task: Omit<Task, 'id' | 'createdAt' | 'status'>) => {
    tasks.value.push({
      ...task,
      id: Date.now().toString(),
      status: 'pending',
      createdAt: new Date().toISOString()
    })
  }

  const updateTaskStatus = (taskId: string, status: Task['status']) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.status = status
      if (status === 'in_progress') {
        activeTask.value = task
      } else if (activeTask.value?.id === taskId) {
        activeTask.value = null
      }
    }
  }

  const addRecommendation = (recommendation: Omit<Recommendation, 'id'>) => {
    recommendations.value.push({
      ...recommendation,
      id: Date.now().toString()
    })
  }

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    currentAgent,
    tasks,
    recommendations,
    isTyping,
    activeTask,
    recentMessages,
    pendingTasks,
    inProgressTasks,
    completedTasks,
    highPriorityRecommendations,
    addMessage,
    setAgent,
    addTask,
    updateTaskStatus,
    addRecommendation,
    clearMessages
  }
})