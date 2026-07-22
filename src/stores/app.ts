import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', () => {
  const currentView = ref<'universe' | 'map' | 'agent' | 'dashboard'>('universe')
  const sidebarOpen = ref(true)
  const theme = ref<'light' | 'dark'>('light')
  const notifications = ref<Array<{
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    message: string
    timestamp: Date
  }>>([])
  
  const panelOpen = ref(false)
  const profileOpen = ref(false)
  const agentOpen = ref(false)
  const panelNodeId = ref<string | null>(null)
  const agentActionTrigger = ref<{ action: string, nodeId: string, timestamp: number } | null>(null)

  // Workspace State
  const isWorkspaceOpen = ref(false)
  const workspaceMode = ref<'teach' | 'practice' | 'code'>('code')

  const openWorkspace = (mode: 'teach' | 'practice' | 'code' = 'code') => {
    workspaceMode.value = mode
    isWorkspaceOpen.value = true
  }

  const closeWorkspace = () => {
    isWorkspaceOpen.value = false
  }

  const openPanel = (nodeId: string) => {
    panelNodeId.value = nodeId
    panelOpen.value = true
  }

  const closePanel = () => {
    panelOpen.value = false
    panelNodeId.value = null
  }

  const toggleProfile = () => {
    profileOpen.value = !profileOpen.value
  }

  const toggleAgent = () => {
    agentOpen.value = !agentOpen.value
  }

  const openAgentWithAction = (action: string, nodeId: string) => {
    agentOpen.value = true
    agentActionTrigger.value = { action, nodeId, timestamp: Date.now() }
  }

  const isDark = computed(() => theme.value === 'dark')

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  const setView = (view: 'universe' | 'map' | 'agent' | 'dashboard') => {
    currentView.value = view
  }

  const addNotification = (type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    notifications.value.push({
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date()
    })
  }

  const removeNotification = (id: string) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return {
    currentView,
    sidebarOpen,
    theme,
    notifications,
    isDark,
    toggleTheme,
    setView,
    addNotification,
    removeNotification,
    panelOpen,
    openPanel,
    closePanel,
    profileOpen,
    toggleProfile,
    agentOpen,
    toggleAgent,
    panelNodeId,
    agentActionTrigger,
    openAgentWithAction,
    isWorkspaceOpen,
    workspaceMode,
    openWorkspace,
    closeWorkspace
  }
})