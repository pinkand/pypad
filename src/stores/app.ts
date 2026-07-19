import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', () => {
  // Layer states
  const panelOpen = ref(false)
  const panelNodeId = ref<string | null>(null)
  const agentOpen = ref(false)
  const profileOpen = ref(false)

  // Theme (defaulting to dark for the 3D universe, but UI is morandi)
  const theme = ref<'light' | 'dark'>('dark')
  
  const notifications = ref<Array<{
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    message: string
    timestamp: Date
  }>>([])

  const isDark = computed(() => theme.value === 'dark')

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  // Panel actions
  const openPanel = (nodeId: string) => {
    panelNodeId.value = nodeId
    panelOpen.value = true
    agentOpen.value = false
    profileOpen.value = false
  }

  const closePanel = () => {
    panelOpen.value = false
    setTimeout(() => {
      panelNodeId.value = null
    }, 300) // wait for animation
  }

  // Agent actions
  const toggleAgent = () => {
    agentOpen.value = !agentOpen.value
    if (agentOpen.value) {
      profileOpen.value = false
    }
  }

  // Profile actions
  const toggleProfile = () => {
    profileOpen.value = !profileOpen.value
    if (profileOpen.value) {
      agentOpen.value = false
    }
  }

  // Notifications
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
    panelOpen,
    panelNodeId,
    agentOpen,
    profileOpen,
    theme,
    notifications,
    isDark,
    toggleTheme,
    openPanel,
    closePanel,
    toggleAgent,
    toggleProfile,
    addNotification,
    removeNotification
  }
})