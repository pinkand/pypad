<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useUserStore } from '@/stores/user'

const appStore = useAppStore()
const knowledgeStore = useKnowledgeStore()
const userStore = useUserStore()

// Account form state
const displayName = ref('')
const email = ref('')
const currentGoal = ref('')

const loadFormState = () => {
  userStore.loadProfile()
  const p = userStore.profile
  if (p) {
    displayName.value = p.name || ''
    email.value = p.email || ''
    currentGoal.value = p.currentGoal || 'Python后端开发'
  }
}

onMounted(loadFormState)
watch(() => appStore.profileOpen, (isOpen) => {
  if (isOpen) loadFormState()
})

const handleSaveProfile = () => {
  userStore.updateProfile({
    name: displayName.value,
    email: email.value,
    currentGoal: currentGoal.value
  })
  appStore.addNotification('success', '账号资料已成功保存！')
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

      <!-- Drawer Scrollable Content -->
      <div class="drawer-content">
        
        <!-- Cognitive Progress -->
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

        <!-- Account Profile Form -->
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

        <!-- Logout -->
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

.drawer-content {
  padding: 20px 24px;
  overflow-y: auto;
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

.form-input {
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

.form-input:focus {
  border-color: var(--info);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
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
