<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useUserStore } from '@/stores/user'

const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()
const userStore = useUserStore()

const activeTab = ref<'profile' | 'ai' | 'system'>('profile')

// Account form state
const displayName = ref('')
const email = ref('')
const currentGoal = ref('')

// AI Config form state
const provider = ref<'openai' | 'deepseek' | 'ollama' | 'mock'>('mock')
const apiKey = ref('')
const baseUrl = ref('')
const model = ref('')
const temperature = ref(0.7)
const maxTokens = ref(1000)
const showApiKey = ref(false)

const loadFormState = () => {
  userStore.loadProfile()
  const p = userStore.profile
  if (p) {
    displayName.value = p.name || ''
    email.value = p.email || ''
    currentGoal.value = p.currentGoal || 'Python后端开发'
  }

  const cfg = userStore.aiConfig
  provider.value = cfg.provider || 'mock'
  apiKey.value = cfg.apiKey || ''
  baseUrl.value = cfg.baseUrl || 'https://api.deepseek.com'
  model.value = cfg.model || 'deepseek-chat'
  temperature.value = cfg.temperature ?? 0.7
  maxTokens.value = cfg.maxTokens ?? 1000
}

onMounted(loadFormState)
watch(() => appStore.profileOpen, (isOpen) => {
  if (isOpen) loadFormState()
})

// Quick provider presets
watch(provider, (newProvider) => {
  if (newProvider === 'deepseek') {
    baseUrl.value = 'https://api.deepseek.com'
    model.value = 'deepseek-chat'
  } else if (newProvider === 'openai') {
    baseUrl.value = 'https://api.openai.com/v1'
    model.value = 'gpt-4o-mini'
  } else if (newProvider === 'ollama') {
    baseUrl.value = 'http://localhost:11434'
    model.value = 'llama3'
  } else if (newProvider === 'mock') {
    baseUrl.value = 'https://api.deepseek.com'
    model.value = 'mock-tutor-v2'
  }
})

const handleSaveProfile = () => {
  userStore.updateProfile({
    name: displayName.value,
    email: email.value,
    currentGoal: currentGoal.value
  })
  appStore.addNotification('success', '账号资料已成功保存！')
}

const handleSaveAiConfig = () => {
  userStore.saveAiConfig({
    provider: provider.value,
    apiKey: apiKey.value,
    baseUrl: baseUrl.value,
    model: model.value,
    temperature: Number(temperature.value),
    maxTokens: Number(maxTokens.value)
  })
  appStore.addNotification('success', `AI 配置已更新：[${provider.value.toUpperCase()}] ${model.value}`)
}

const overallProgress = computed(() => {
  const nodes = knowledgeStore.nodes
  if (nodes.length === 0) return 0
  const totalMastery = nodes.reduce((sum, n) => sum + (knowledgeStore.getNodeMastery(n.id) || 0), 0)
  return Math.round(totalMastery / nodes.length)
})

const handleLogout = () => {
  userStore.logout()
  appStore.toggleProfile()
  appStore.addNotification('info', '已安全退出登录')
}
</script>

<template>
  <Transition name="slide-fade-up">
    <div v-if="appStore.profileOpen" class="profile-drawer glass">
      
      <!-- Drawer Header -->
      <div class="drawer-header">
        <div class="user-info">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" class="avatar-large" />
          <div class="user-details">
            <h2 class="username">{{ userStore.profile?.name || 'Python 学习者' }}</h2>
            <span class="level">Level {{ userStore.profile?.level || 1 }} 知识探索者</span>
          </div>
        </div>
        <button class="close-btn" @click="appStore.toggleProfile()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Navigation Tabs -->
      <div class="drawer-tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">
          👤 资料
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'">
          🤖 AI 配置
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'system' }" @click="activeTab = 'system'">
          ⚙️ 设置
        </button>
      </div>

      <!-- Drawer Scrollable Content -->
      <div class="drawer-content">
        
        <!-- Tab 1: User Profile -->
        <div v-show="activeTab === 'profile'" class="tab-pane">
          <section class="section">
            <h3 class="section-title">Cognitive Progress</h3>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" :style="{ width: `${overallProgress}%` }"></div>
            </div>
            <div class="progress-text">
              <span>全局知识掌握度</span>
              <span class="font-mono">{{ overallProgress }}%</span>
            </div>
          </section>

          <section class="section form-section">
            <h3 class="section-title">账号资料修改</h3>
            <div class="form-group">
              <label class="form-label">用户昵称</label>
              <input v-model="displayName" type="text" class="form-input" placeholder="输入您的名称" />
            </div>

            <div class="form-group">
              <label class="form-label">绑定邮箱</label>
              <input v-model="email" type="email" class="form-input" placeholder="user@example.com" />
            </div>

            <div class="form-group">
              <label class="form-label">当前学习目标</label>
              <input v-model="currentGoal" type="text" class="form-input" placeholder="如：Python后端与大模型开发" />
            </div>

            <button class="save-btn btn-primary" @click="handleSaveProfile">
              保存资料修改
            </button>
          </section>
        </div>

        <!-- Tab 2: AI Configuration -->
        <div v-show="activeTab === 'ai'" class="tab-pane">
          <section class="section form-section">
            <div class="section-header-flex">
              <h3 class="section-title">AI 大模型全局配置</h3>
              <span class="current-provider-badge">{{ provider.toUpperCase() }}</span>
            </div>

            <!-- Provider Selection -->
            <div class="form-group">
              <label class="form-label">服务提供商 (Provider)</label>
              <select v-model="provider" class="form-select">
                <option value="mock">Mock 模拟模式 (免 Key 调试)</option>
                <option value="deepseek">DeepSeek (强烈推荐)</option>
                <option value="openai">OpenAI (官方/代理接口)</option>
                <option value="ollama">Ollama (本地私有化大模型)</option>
              </select>
            </div>

            <!-- API Key Input with Eye Toggle -->
            <div class="form-group" v-if="provider !== 'ollama' && provider !== 'mock'">
              <label class="form-label">API Key 密钥</label>
              <div class="input-password-wrapper">
                <input 
                  v-model="apiKey" 
                  :type="showApiKey ? 'text' : 'password'" 
                  class="form-input" 
                  placeholder="sk-..."
                />
                <button class="toggle-eye-btn" @click="showApiKey = !showApiKey">
                  <svg v-if="!showApiKey" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Base URL Input -->
            <div class="form-group">
              <label class="form-label">API Base URL (接口端点)</label>
              <input v-model="baseUrl" type="text" class="form-input" placeholder="https://api.deepseek.com" />
            </div>

            <!-- Model Name Input -->
            <div class="form-group">
              <label class="form-label">模型代号 (Model Name)</label>
              <input v-model="model" type="text" class="form-input" placeholder="deepseek-chat / gpt-4o-mini" />
            </div>

            <!-- Temperature Slider -->
            <div class="form-group">
              <div class="flex-between">
                <label class="form-label">创造力 Temperature</label>
                <span class="font-mono text-xs">{{ temperature }}</span>
              </div>
              <input v-model.number="temperature" type="range" min="0" max="1" step="0.1" class="form-range" />
            </div>

            <button class="save-btn btn-primary" @click="handleSaveAiConfig">
              测试并保存全局 AI 配置
            </button>
          </section>
        </div>

        <!-- Tab 3: System & Theme -->
        <div v-show="activeTab === 'system'" class="tab-pane">
          <section class="section">
            <h3 class="section-title">系统偏好</h3>
            
            <div class="form-group mb-4">
              <label class="form-label">背景画风与动画 (Background Animation)</label>
              <select 
                :value="appStore.bgAnimationStyle" 
                @change="(e: any) => appStore.setBgAnimationStyle(e.target.value)" 
                class="form-select"
              >
                <option value="cosmic">🌌 高阶弥散流光 (发光粒子 + 弥散光晕)</option>
                <option value="slate">⚪ 原版极简画风 (Slate 灰蓝粒子 + 纯净画布)</option>
              </select>
            </div>

            <button class="menu-btn" @click="appStore.toggleTheme()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path v-if="appStore.isDark" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                <path v-else d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              {{ appStore.isDark ? '切换至浅色模式' : '切换至暗色模式' }}
            </button>
          </section>

          <section class="section">
            <div class="flex-between">
              <h3 class="section-title">系统通知</h3>
              <span class="badge" v-if="appStore.notifications.length">{{ appStore.notifications.length }}</span>
            </div>
            
            <div v-if="appStore.notifications.length === 0" class="empty-state">
              暂无新通知
            </div>
            
            <ul class="notification-list" v-else>
              <li v-for="notif in appStore.notifications.slice(0, 3)" :key="notif.id" class="notif-item">
                <span class="notif-dot" :class="`notif-${notif.type}`"></span>
                <p class="notif-msg">{{ notif.message }}</p>
              </li>
            </ul>
          </section>

          <section class="section">
            <button class="menu-btn text-danger" @click="handleLogout">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              退出当前账号
            </button>
          </section>
        </div>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
.profile-drawer {
  position: absolute;
  bottom: 96px;
  left: 32px;
  width: 380px;
  border-radius: var(--radius-xl);
  z-index: 55;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: calc(100vh - 120px);
  box-shadow: var(--shadow-glass);
}

.drawer-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.85);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar-large {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border);
}

.username {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.level {
  font-size: 12px;
  color: var(--status-learning);
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.drawer-tabs {
  display: flex;
  background: var(--bg-tertiary);
  padding: 4px 12px;
  gap: 6px;
  border-bottom: 1px solid var(--border);
}

.tab-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--bg-primary);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.drawer-content {
  padding: 20px 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  font-weight: 700;
  margin-bottom: 12px;
}

.section-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-provider-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  background: rgba(0, 122, 255, 0.1);
  color: var(--info);
  border-radius: 6px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input, .form-select {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
}

.form-input:focus, .form-select:focus {
  border-color: var(--info);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.input-password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-eye-btn {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 2px;
}

.form-range {
  width: 100%;
  accent-color: var(--accent);
  cursor: pointer;
}

.save-btn {
  width: 100%;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  margin-top: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background-color: var(--accent);
  color: #fff;
}

.btn-primary:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
}

/* Progress */
.progress-bar-bg {
  height: 8px;
  background-color: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-bar-fill {
  height: 100%;
  background-color: var(--status-learning);
  border-radius: 4px;
  transition: width 0.6s ease-out;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
}

.menu-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  text-align: left;
}

.menu-btn:hover {
  background: var(--bg-tertiary);
}

.text-danger {
  color: var(--danger);
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
}

.notification-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notif-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.notif-info { background-color: var(--status-learning); }
.notif-success { background-color: var(--success); }
.notif-warning { background-color: var(--warning); }
.notif-error { background-color: var(--danger); }

.notif-msg {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
}

.slide-fade-up-enter-active,
.slide-fade-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom left;
}

.slide-fade-up-enter-from,
.slide-fade-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
