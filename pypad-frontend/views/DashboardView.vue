<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useUserStore } from '@/stores/user'
import { dashboardApi, analyticsApi, userApi } from '@/services/api'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()
const userStore = useUserStore()

const loading = ref(true)
const dashboardData = ref<any>(null)
const analyticsData = ref<any>(null)
const recommendPath = ref<any[]>([])

const masteredCount = computed(() => analyticsData.value?.masteredNodes || 0)
const totalNodes = computed(() => analyticsData.value?.totalNodes || 0)
const avgMastery = computed(() => analyticsData.value?.averageMastery || 0)
const streak = computed(() => dashboardData.value?.studyStreakDays || 0)
const totalStudyTime = computed(() => {
  const sec = dashboardData.value?.totalStudyTimeSeconds || 0
  if (sec < 60) return `${sec}秒`
  if (sec < 3600) return `${Math.floor(sec / 60)}分钟`
  return `${(sec / 3600).toFixed(1)}小时`
})
const weakNodeIds = computed(() => dashboardData.value?.weakKnowledgeNodeIds || [])

const masteryPercent = computed(() => {
  if (totalNodes.value === 0) return 0
  return Math.round((masteredCount.value / totalNodes.value) * 100)
})

const weakNodes = computed(() => {
  return weakNodeIds.value
    .map((id: string) => knowledgeStore.getNodeById(id))
    .filter(Boolean)
    .slice(0, 5)
})

onMounted(async () => {
  try {
    const userId = userStore.authUser?.id
    const [overview, analytics] = await Promise.all([
      dashboardApi.getOverview(userId),
      analyticsApi.getOverview(userId),
    ])
    dashboardData.value = overview
    analyticsData.value = analytics

    try {
      const pathRes: any = await fetch('http://localhost:8000/api/user/recommend-path', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      }).then(r => r.json())
      recommendPath.value = pathRes?.recommendedPath || pathRes?.path || []
    } catch { /* silent */ }
  } catch (err) {
    console.error('Dashboard load failed:', err)
  } finally {
    loading.value = false
  }
})

const goToNode = (nodeId: string) => {
  router.push({ path: '/map', query: { nodeId } })
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="dashboard-view">
    <!-- Header -->
    <header class="dash-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <div>
          <h1>学习仪表盘</h1>
          <p class="subtitle">你的 Python 学习进度概览</p>
        </div>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Content -->
    <div v-else class="dash-content">
      <!-- Stat Cards Row -->
      <div class="stat-cards">
        <div class="stat-card glass-card">
          <div class="stat-icon" style="background: rgba(99,102,241,0.1); color: #6366f1;">📚</div>
          <div class="stat-info">
            <span class="stat-value">{{ masteredCount }} / {{ totalNodes }}</span>
            <span class="stat-label">已掌握知识点</span>
          </div>
        </div>

        <div class="stat-card glass-card">
          <div class="stat-icon" style="background: rgba(16,185,129,0.1); color: #10b981;">📈</div>
          <div class="stat-info">
            <span class="stat-value">{{ avgMastery.toFixed(1) }}%</span>
            <span class="stat-label">平均掌握度</span>
          </div>
        </div>

        <div class="stat-card glass-card">
          <div class="stat-icon" style="background: rgba(245,158,11,0.1); color: #f59e0b;">🔥</div>
          <div class="stat-info">
            <span class="stat-value">{{ streak }} 天</span>
            <span class="stat-label">学习连续天数</span>
          </div>
        </div>

        <div class="stat-card glass-card">
          <div class="stat-icon" style="background: rgba(59,130,246,0.1); color: #3b82f6;">⏱️</div>
          <div class="stat-info">
            <span class="stat-value">{{ totalStudyTime }}</span>
            <span class="stat-label">累计学习时长</span>
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="section-card glass-card">
        <h3>📊 全局掌握度</h3>
        <div class="progress-bar-container">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ width: masteryPercent + '%' }"></div>
          </div>
          <span class="progress-text">{{ masteryPercent }}%</span>
        </div>
        <div class="mastery-breakdown">
          <span class="breakdown-item mastered">已掌握 {{ masteredCount }}</span>
          <span class="breakdown-item learning">学习中 {{ (analyticsData?.totalNodes || 0) - masteredCount }}</span>
          <span class="breakdown-item weak">薄弱 {{ weakNodeIds.length }}</span>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="two-col">
        <!-- Weak Points -->
        <div class="section-card glass-card">
          <h3>⚠️ 薄弱知识点</h3>
          <div v-if="weakNodes.length === 0" class="empty-msg">暂无薄弱知识点，继续保持！</div>
          <div v-else class="node-list">
            <div
              v-for="node in weakNodes"
              :key="node.id"
              class="node-item"
              @click="goToNode(node.id)"
            >
              <div class="node-dot weak"></div>
              <div class="node-info">
                <span class="node-name">{{ node.name }}</span>
                <span class="node-cat">{{ node.category }}</span>
              </div>
              <span class="node-mastery">{{ knowledgeStore.getNodeMastery(node.id) }}%</span>
            </div>
          </div>
        </div>

        <!-- Recommended Path -->
        <div class="section-card glass-card">
          <h3>🗺️ 推荐学习路径</h3>
          <div v-if="recommendPath.length === 0" class="empty-msg">暂无推荐路径</div>
          <div v-else class="path-list">
            <div
              v-for="(nodeId, idx) in recommendPath.slice(0, 8)"
              :key="nodeId"
              class="path-item"
              @click="goToNode(nodeId)"
            >
              <span class="path-num">{{ idx + 1 }}</span>
              <span class="path-name">{{ knowledgeStore.getNodeById(nodeId)?.name || nodeId }}</span>
              <span class="path-mastery">{{ knowledgeStore.getNodeMastery(nodeId) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-view {
  width: 100vw;
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 0 0 60px;
  overflow-y: auto;
}

.dash-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.back-btn {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  transition: all 0.2s;
}
.back-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.dash-content {
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: var(--text-secondary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.glass-card {
  background: rgba(255,255,255,0.7);
  border: 1px solid var(--border);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.stat-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.section-card {
  padding: 24px;
}

.section-card h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar-bg {
  flex: 1;
  height: 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 6px;
  transition: width 0.8s ease;
}

.progress-text {
  font-size: 18px;
  font-weight: 700;
  color: #6366f1;
  min-width: 48px;
}

.mastery-breakdown {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}

.breakdown-item {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 99px;
}

.breakdown-item.mastered {
  background: rgba(16,185,129,0.1);
  color: #10b981;
}
.breakdown-item.learning {
  background: rgba(59,130,246,0.1);
  color: #3b82f6;
}
.breakdown-item.weak {
  background: rgba(239,68,68,0.1);
  color: #ef4444;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.empty-msg {
  color: var(--text-secondary);
  font-size: 14px;
  text-align: center;
  padding: 24px 0;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
}
.node-item:hover {
  background: var(--bg-secondary);
}

.node-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.node-dot.weak { background: #ef4444; }
.node-dot.learning { background: #3b82f6; }
.node-dot.mastered { background: #10b981; }

.node-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.node-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.node-cat {
  font-size: 11px;
  color: var(--text-secondary);
}

.node-mastery {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.path-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
}
.path-item:hover {
  background: var(--bg-secondary);
}

.path-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #6366f1;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.path-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.path-mastery {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
  .two-col { grid-template-columns: 1fr; }
}
</style>
