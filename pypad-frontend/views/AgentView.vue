<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { agentApi } from '@/services/api'
import { useUserStore } from '@/stores/user'
import { useKnowledgeStore } from '@/stores/knowledge'

const router = useRouter()
const userStore = useUserStore()
const knowledgeStore = useKnowledgeStore()

type AgentType = 'tutor' | 'practice' | 'coder' | 'planner' | 'memory'
const currentAgent = ref<AgentType>('tutor')
const messages = ref<Array<{ role: 'user' | 'assistant'; content: string; timestamp: string }>>([])
const inputText = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const agentLabels: Record<AgentType, { name: string; icon: string; desc: string }> = {
  tutor: { name: 'AI 导师', icon: '🎓', desc: '讲解知识点，解答学习疑惑' },
  practice: { name: '练习生成器', icon: '✏️', desc: '生成练习题，提供解题提示' },
  coder: { name: '代码分析师', icon: '💻', desc: '分析代码，提供优化建议' },
  planner: { name: '学习规划师', icon: '📋', desc: '制定学习计划，规划学习路径' },
  memory: { name: '记忆管理器', icon: '🧠', desc: '分析薄弱点，推荐复习内容' },
}

const agentTabs: AgentType[] = ['tutor', 'practice', 'coder', 'planner', 'memory']

const quickChips: Record<AgentType, string[]> = {
  tutor: ['解释 Python 变量', '什么是列表推导式', '函数参数传递机制'],
  practice: ['生成一道循环练习题', '出一道字典操作题', '函数综合练习'],
  coder: ['优化这段代码', '这段代码有什么问题', '如何更 Pythonic'],
  planner: ['制定 Python 学习计划', '我应该先学什么', '30天学习路线'],
  memory: ['我哪些知识点薄弱', '推荐复习内容', '学习进度分析'],
}

onMounted(async () => {
  await loadHistory()
})

const loadHistory = async () => {
  try {
    const res: any = await agentApi.getHistory(currentAgent.value)
    messages.value = (res?.messages || []).map((m: any) => ({
      role: m.role,
      content: m.content,
      timestamp: m.createdAt || new Date().toISOString(),
    }))
    await nextTick()
    scrollToBottom()
  } catch { /* silent */ }
}

watch(currentAgent, async () => {
  messages.value = []
  await loadHistory()
})

const sendMessage = async (text?: string) => {
  const msg = text || inputText.value.trim()
  if (!msg) return

  inputText.value = ''
  messages.value.push({ role: 'user', content: msg, timestamp: new Date().toISOString() })
  await nextTick()
  scrollToBottom()

  isTyping.value = true
  try {
    const res: any = await agentApi.chat({
      message: msg,
      agentType: currentAgent.value,
      knowledgeId: undefined,
    })
    messages.value.push({
      role: 'assistant',
      content: res?.message || '抱歉，暂时无法回答。',
      timestamp: new Date().toISOString(),
    })
  } catch (err) {
    messages.value.push({
      role: 'assistant',
      content: '请求失败，请检查后端服务。',
      timestamp: new Date().toISOString(),
    })
  } finally {
    isTyping.value = false
    await nextTick()
    scrollToBottom()
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="agent-view">
    <header class="view-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h1>AI 导师</h1>
      </div>
    </header>

    <div class="agent-body">
      <!-- Agent Tabs -->
      <aside class="agent-sidebar glass-card">
        <div class="sidebar-section">
          <h3>选择 AI 角色</h3>
          <div class="agent-tabs">
            <button
              v-for="agent in agentTabs"
              :key="agent"
              class="agent-tab"
              :class="{ active: currentAgent === agent }"
              @click="currentAgent = agent"
            >
              <span class="tab-icon">{{ agentLabels[agent].icon }}</span>
              <div class="tab-info">
                <span class="tab-name">{{ agentLabels[agent].name }}</span>
                <span class="tab-desc">{{ agentLabels[agent].desc }}</span>
              </div>
            </button>
          </div>
        </div>
      </aside>

      <!-- Chat Area -->
      <main class="chat-area glass-card">
        <!-- Messages -->
        <div ref="messagesContainer" class="messages-container">
          <!-- Empty State -->
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">{{ agentLabels[currentAgent].icon }}</div>
            <h3>{{ agentLabels[currentAgent].name }}</h3>
            <p>{{ agentLabels[currentAgent].desc }}</p>
            <div class="quick-chips">
              <button
                v-for="chip in quickChips[currentAgent]"
                :key="chip"
                class="chip"
                @click="sendMessage(chip)"
              >
                {{ chip }}
              </button>
            </div>
          </div>

          <!-- Messages -->
          <div v-for="(msg, idx) in messages" :key="idx" class="message-row" :class="msg.role">
            <div v-if="msg.role === 'assistant'" class="msg-avatar">{{ agentLabels[currentAgent].icon }}</div>
            <div class="bubble" :class="msg.role">
              <div class="bubble-content">{{ msg.content }}</div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="message-row assistant">
            <div class="msg-avatar">{{ agentLabels[currentAgent].icon }}</div>
            <div class="bubble assistant typing-bubble">
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="input-area">
          <div class="quick-actions" v-if="messages.length > 0">
            <button
              v-for="chip in quickChips[currentAgent].slice(0, 3)"
              :key="chip"
              class="chip small"
              @click="sendMessage(chip)"
            >
              {{ chip }}
            </button>
          </div>
          <div class="input-wrapper">
            <textarea
              v-model="inputText"
              @keydown="handleKeydown"
              placeholder="输入你的问题..."
              rows="1"
            ></textarea>
            <button class="send-btn" @click="sendMessage()" :disabled="!inputText.trim()">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.agent-view {
  width: 100vw; height: 100vh; background: var(--bg-primary);
  display: flex; flex-direction: column; overflow: hidden;
}

.view-header {
  padding: 12px 32px; background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0; }

.back-btn {
  background: transparent; border: 1px solid var(--border); border-radius: 8px;
  padding: 6px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; transition: all 0.2s;
}
.back-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.agent-body {
  flex: 1; display: flex; gap: 16px; padding: 16px; overflow: hidden;
}

.glass-card {
  background: rgba(255,255,255,0.7); border: 1px solid var(--border);
  border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.agent-sidebar {
  width: 260px; padding: 20px; flex-shrink: 0; overflow-y: auto;
}

.sidebar-section h3 {
  font-size: 12px; font-weight: 700; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 12px;
}

.agent-tabs { display: flex; flex-direction: column; gap: 6px; }

.agent-tab {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  border: 1px solid transparent; background: transparent;
  cursor: pointer; transition: all 0.15s; text-align: left;
}
.agent-tab:hover { background: var(--bg-secondary); }
.agent-tab.active { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.2); }

.tab-icon { font-size: 20px; flex-shrink: 0; }
.tab-info { display: flex; flex-direction: column; }
.tab-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.tab-desc { font-size: 11px; color: var(--text-secondary); }

.chat-area {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
}

.messages-container {
  flex: 1; overflow-y: auto; padding: 24px;
  display: flex; flex-direction: column; gap: 16px;
}

.empty-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0 0 4px; }
.empty-state p { font-size: 14px; color: var(--text-secondary); margin: 0 0 20px; }

.quick-chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }

.chip {
  padding: 6px 14px; border-radius: 99px;
  border: 1px solid var(--border); background: rgba(255,255,255,0.8);
  font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all 0.15s;
}
.chip:hover { border-color: var(--accent); color: var(--accent); background: rgba(99,102,241,0.05); }
.chip.small { font-size: 12px; padding: 4px 10px; }

.message-row {
  display: flex; gap: 10px; max-width: 80%;
}
.message-row.user { align-self: flex-end; flex-direction: row-reverse; }
.message-row.assistant { align-self: flex-start; }

.msg-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(99,102,241,0.1); display: flex;
  align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;
}

.bubble {
  padding: 12px 16px; border-radius: 16px; font-size: 14px; line-height: 1.6;
}
.bubble.user {
  background: var(--accent); color: #fff;
  border-bottom-right-radius: 4px;
}
.bubble.assistant {
  background: rgba(255,255,255,0.9); color: var(--text-primary);
  border: 1px solid var(--border); border-bottom-left-radius: 4px;
}

.bubble-content { white-space: pre-wrap; word-break: break-word; }

.typing-bubble { padding: 12px 20px; }
.typing-dots { display: flex; gap: 4px; }
.typing-dots span {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--text-secondary); animation: bounce 1.4s infinite ease-in-out;
}
.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

.input-area {
  padding: 16px 24px; border-top: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 8px;
}

.quick-actions { display: flex; gap: 6px; flex-wrap: wrap; }

.input-wrapper {
  display: flex; align-items: flex-end; gap: 8px;
  background: rgba(255,255,255,0.8); border: 1px solid var(--border);
  border-radius: 12px; padding: 8px 12px;
}

.input-wrapper textarea {
  flex: 1; border: none; background: transparent; resize: none;
  font-size: 14px; line-height: 1.5; color: var(--text-primary);
  outline: none; min-height: 24px; max-height: 120px;
  font-family: inherit;
}

.send-btn {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--accent); color: #fff; border: none;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; flex-shrink: 0;
}
.send-btn:hover { background: var(--accent-hover); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
