<script setup lang="ts">
import { ref, nextTick, watch, computed, onMounted } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useAppStore } from '@/stores/app'
import { AGENT_LABELS } from '@/utils/constants'
import type { AgentType } from '@/types/agent'
import { agentApi } from '@/services/api'

import { useUserStore } from '@/stores/user'

const agentStore = useAgentStore()
const knowledgeStore = useKnowledgeStore()
const appStore = useAppStore()
const userStore = useUserStore()

const inputMessage = ref('')
const messagesContainerRef = ref<HTMLDivElement>()
const isThinking = ref(false)

// Scroll to bottom
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainerRef.value) {
    messagesContainerRef.value.scrollTo({ top: messagesContainerRef.value.scrollHeight, behavior: 'smooth' })
  }
}

watch(() => agentStore.messages.length, scrollToBottom)

// Agent configs with colors and icons
const agentConfigs: Record<AgentType, { icon: string; color: string; label: string }> = {
  tutor:    { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>', color: '#6366f1', label: '知识导师' },
  practice: { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>', color: '#10b981', label: '练习生成' },
  coder:    { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>', color: '#3b82f6', label: '代码分析' },
  planner:  { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>', color: '#f59e0b', label: '学习规划' },
  memory:   { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>', color: '#8b5cf6', label: '记忆管理' }
}

const currentAgent = computed(() => agentConfigs[agentStore.currentAgent] || agentConfigs.tutor)

// Send message
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isThinking.value) return

  agentStore.addMessage('user', message)
  inputMessage.value = ''
  isThinking.value = true

  // Pre-add assistant placeholder message for progressive typing
  agentStore.addMessage('assistant', '')

  try {
    const token = localStorage.getItem('auth_token')
    const resp = await fetch('http://localhost:8000/api/agent/chat-stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        message,
        agentType: agentStore.currentAgent,
        knowledgeId: knowledgeStore.selectedNode?.id,
        aiConfig: userStore.aiConfig
      })
    })

    if (!resp.ok || !resp.body) {
      throw new Error('SSE stream connection failed')
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let accumulated = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const chunk = line.substring(6)
          if (chunk === '[DONE]') break
          accumulated += chunk
          agentStore.updateLastMessage(accumulated)
        }
      }
    }

    if (!accumulated) {
      agentStore.updateLastMessage(generateLocalResponse(message))
    }
  } catch (error) {
    // 接口不可用时使用静态响应进行渐进模拟
    const fallback = generateLocalResponse(message)
    agentStore.updateLastMessage(fallback)
  } finally {
    isThinking.value = false
  }
}


// Local fallback response
const generateLocalResponse = (userMessage: string): string => {
  const selectedNode = knowledgeStore.selectedNode
  const currentAgent = agentStore.currentAgent

  switch (currentAgent) {
    case 'tutor':
      if (selectedNode) {
        return `📚 **${selectedNode.name}**\n\n${selectedNode.description}\n\n**学习要点：**\n1. 理解核心概念\n2. 掌握基本语法\n3. 实践应用\n\n**当前掌握度：** ${knowledgeStore.getNodeMastery(selectedNode.id)}%\n\n需要我详细讲解某个部分吗？`
      }
      break
    case 'practice':
      if (selectedNode) {
        return `📝 **练习生成器**\n\n我将为"${selectedNode.name}"生成练习题：\n\n**题目类型：**\n- 选择题\n- 填空题\n- 编程题\n\n**难度级别：**\n- 基础\n- 中等\n- 进阶\n\n请选择你想要的练习类型和难度。`
      }
      break
    case 'coder':
      return `💻 **代码分析师**\n\n我可以帮你：\n- 分析代码逻辑\n- 找出潜在问题\n- 优化代码性能\n- 解释代码功能\n\n请粘贴你想要分析的代码。`
    case 'planner':
      return `📋 **学习规划师**\n\n我可以帮你制定学习计划：\n\n1. **评估当前水平**\n2. **设定学习目标**\n3. **制定学习路径**\n4. **安排学习时间**\n\n请告诉我你的学习目标是什么？`
    case 'memory':
      return `🧠 **记忆管理器**\n\n我可以帮你：\n- 复习容易忘记的知识点\n- 分析错误模式\n- 优化学习方法\n- 追踪学习进度\n\n让我查看你的学习记录...`
  }

  return `你好！我是${AGENT_LABELS[currentAgent as AgentType]}。\n\n我可以帮助你：\n- 解答Python相关问题\n- 生成练习题\n- 分析代码\n- 制定学习计划\n\n请告诉我你想学习什么？`
}

// Quick actions
const quickActions = [
  { label: '解释知识点', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>', action: 'explain' },
  { label: '生成练习', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>', action: 'practice' },
  { label: '分析代码', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>', action: 'analyze' },
  { label: '制定计划', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>', action: 'plan' }
]

const handleQuickAction = (action: string) => {
  const selectedNode = knowledgeStore.selectedNode
  switch (action) {
    case 'explain':
      inputMessage.value = selectedNode ? `请详细解释"${selectedNode.name}"这个知识点` : '请解释Python的核心概念'
      break
    case 'practice':
      inputMessage.value = selectedNode ? `请为"${selectedNode.name}"生成练习题` : '请生成Python基础练习题'
      break
    case 'analyze':
      inputMessage.value = '请分析这段代码：\n```python\n# 在这里粘贴代码\n```'
      break
    case 'plan':
      inputMessage.value = '请帮我制定Python学习计划'
      break
  }
  sendMessage()
}

watch(() => appStore.agentActionTrigger, (trigger) => {
  if (trigger) {
    if (trigger.action === 'explain') agentStore.setAgent('tutor')
    if (trigger.action === 'practice') agentStore.setAgent('practice')
    if (trigger.action === 'analyze') agentStore.setAgent('coder')
    if (trigger.action === 'plan') agentStore.setAgent('planner')
    
    const node = knowledgeStore.getNodeById(trigger.nodeId)
    if (node) {
      knowledgeStore.selectNode(node)
      // Small delay to ensure agent UI transitions before sending message
      setTimeout(() => {
        handleQuickAction(trigger.action)
      }, 300)
    }
  }
}, { deep: true })

// 加载当前 agent 类型的聊天历史
onMounted(() => {
  agentStore.loadHistory()
})

// 切换 agent 类型时加载对应历史
watch(() => agentStore.currentAgent, (newAgent) => {
  agentStore.loadHistory(newAgent)
})

const clearChat = () => agentStore.clearMessages()

// Handle enter key (shift+enter = newline)
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div class="chat-window">
    <!-- Header -->
    <div class="chat-header">
      <div class="agent-info">
        <div
          class="agent-avatar"
          :style="{ background: `linear-gradient(135deg, ${currentAgent.color}33, ${currentAgent.color}11)`, borderColor: `${currentAgent.color}44`, color: currentAgent.color }"
          v-html="currentAgent.icon"
        >
        </div>
        <div class="agent-meta">
          <span class="agent-name">{{ currentAgent.label }}</span>
          <span class="agent-status">
            <span class="status-dot" :style="{ background: currentAgent.color }" />
            在线
          </span>
        </div>
      </div>

      <div class="chat-actions">
        <!-- Agent switcher -->
        <div class="agent-tabs">
          <button
            v-for="(config, key) in agentConfigs"
            :key="key"
            class="agent-tab"
            :class="{ 'agent-tab--active': agentStore.currentAgent === key }"
            :style="agentStore.currentAgent === key ? { color: config.color, borderColor: config.color + '60' } : {}"
            @click="agentStore.setAgent(key as AgentType)"
            :title="config.label"
            v-html="config.icon"
          >
          </button>
        </div>

        <!-- Clear button -->
        <button class="clear-btn" @click="clearChat" title="清空对话">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div ref="messagesContainerRef" class="messages-area">
      <!-- Empty state -->
      <div v-if="agentStore.messages.length === 0" class="empty-chat">
        <div class="empty-orb" :style="{ background: `radial-gradient(circle, ${currentAgent.color}30, transparent)`, color: currentAgent.color }">
          <span class="empty-icon" v-html="currentAgent.icon"></span>
        </div>
        <h3 class="empty-title">{{ currentAgent.label }}</h3>
        <p class="empty-desc">开始与 AI 助手对话，探索 Python 知识宇宙</p>
        <div class="quick-chips">
          <button
            v-for="action in quickActions"
            :key="action.action"
            class="quick-chip"
            @click="handleQuickAction(action.action)"
          >
            <span class="chip-icon" v-html="action.icon"></span>
            <span>{{ action.label }}</span>
          </button>
        </div>
      </div>

      <!-- Message list -->
      <TransitionGroup name="message" tag="div" class="message-list">
        <div
          v-for="message in agentStore.recentMessages"
          :key="message.id"
          class="message-row"
          :class="message.role === 'user' ? 'message-row--user' : 'message-row--ai'"
        >
          <!-- AI avatar -->
          <div v-if="message.role !== 'user'" class="msg-avatar" :style="{ color: currentAgent.color }">
            <span class="msg-avatar-icon" v-html="currentAgent.icon"></span>
          </div>

          <!-- Bubble -->
          <div class="bubble" :class="message.role === 'user' ? 'bubble--user' : 'bubble--ai'">
            <div class="bubble-content whitespace-pre-wrap">{{ message.content }}</div>
            <div class="bubble-time">
              {{ new Date(message.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}
            </div>
          </div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isThinking" key="thinking" class="message-row message-row--ai">
          <div class="msg-avatar" :style="{ color: currentAgent.color }">
            <span class="msg-avatar-icon" v-html="currentAgent.icon"></span>
          </div>
          <div class="bubble bubble--ai typing-bubble">
            <div class="typing-dots">
              <div class="typing-dot" />
              <div class="typing-dot" />
              <div class="typing-dot" />
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Input area -->
    <div class="input-area">
      <!-- Quick action chips (when there are messages) -->
      <div v-if="agentStore.messages.length > 0" class="quick-actions-row">
        <button
          v-for="action in quickActions"
          :key="action.action"
          class="quick-chip"
          @click="handleQuickAction(action.action)"
        >
          <span class="chip-icon" v-html="action.icon"></span>
          <span>{{ action.label }}</span>
        </button>
      </div>

      <!-- Text input + send -->
      <div class="input-row">
        <div class="input-wrapper" :class="{ 'input-wrapper--focus': inputMessage.length > 0 }">
          <textarea
            v-model="inputMessage"
            @keydown="handleKeydown"
            placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
            class="chat-input"
            rows="1"
          />
        </div>
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isThinking"
          :style="inputMessage.trim() ? { boxShadow: '0 4px 16px rgba(0, 122, 255, 0.4)' } : {}"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.agent-meta {
  display: flex;
  flex-direction: column;
}

.agent-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-secondary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: glow-pulse 2s ease-in-out infinite;
}

/* Actions */
.chat-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agent-tabs {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 3px;
}

.agent-tab {
  width: 28px;
  height: 28px;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: var(--text-secondary);
}

.agent-tab:hover {
  background: rgba(99, 102, 241, 0.1);
}

.agent-tab--active {
  background: rgba(99, 102, 241, 0.15) !important;
  border-color: inherit !important;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.08);
}

/* Messages */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Empty state */
.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  gap: 12px;
  padding: 24px;
  text-align: center;
}

.empty-orb {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 4s ease-in-out infinite;
}

.empty-icon {
  font-size: 36px;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 280px;
  line-height: 1.5;
}

/* Quick chips */
.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 8px;
}

.quick-chip {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--border);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

:deep(.chip-icon) {
  display: flex;
  align-items: center;
}

:deep(.chip-icon svg) {
  width: 14px;
  height: 14px;
}

.quick-chip:hover {
  color: var(--text-primary);
  border-color: rgba(99, 102, 241, 0.3);
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

/* Message rows */
.message-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.message-row--user {
  justify-content: flex-end;
}

.message-row--ai {
  justify-content: flex-start;
}

/* AI avatar in messages */
.msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(12px);
}

:deep(.msg-avatar-icon svg) {
  width: 16px;
  height: 16px;
}

/* Bubbles */
.bubble {
  max-width: 78%;
  padding: 10px 14px;
  position: relative;
}

.bubble--user {
  background: rgba(0, 122, 255, 0.85); /* Apple Blue Glass */
  border-radius: 16px 16px 4px 16px;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2);
  color: white;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.bubble--ai {
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--border);
  border-radius: 16px 16px 16px 4px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  color: var(--text-primary);
  box-shadow: var(--shadow-glass);
}

.bubble-content {
  font-size: 13px;
  line-height: 1.6;
}

.bubble-time {
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.5;
  text-align: right;
}

/* Typing */
.typing-bubble {
  padding: 12px 16px;
}

.typing-dots {
  display: flex;
  gap: 5px;
  align-items: center;
}

/* Input area */
.input-area {
  padding: 12px 16px;
  border-top: 1px solid rgba(99, 102, 241, 0.12);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-wrapper {
  flex: 1;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--border);
  border-radius: 12px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.input-wrapper--focus {
  border-color: rgba(0, 122, 255, 0.4);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
  background: rgba(255, 255, 255, 0.85);
}

.chat-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  resize: none;
  padding: 10px 14px;
  line-height: 1.5;
  max-height: 120px;
  overflow-y: auto;
}

.chat-input::placeholder {
  color: var(--text-tertiary);
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: none;
  background: var(--info);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  box-shadow: none !important;
}

.send-btn:not(:disabled):hover {
  transform: scale(1.06);
  filter: brightness(1.15);
}

/* Message animations */
.message-enter-active {
  animation: slide-up 0.25s ease-out both;
}
.message-leave-active {
  animation: fade-in 0.2s ease-out reverse;
}
</style>