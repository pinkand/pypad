<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { analyticsApi, userApi } from '@/services/api'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()
const userStore = useUserStore()
const loading = ref(true)
const analytics = ref<any>(null)
const studyRecords = ref<any[]>([])

onMounted(async () => {
  try {
    const userId = userStore.authUser?.id
    const [analyticsRes, recordsRes] = await Promise.all([
      analyticsApi.getOverview(userId),
      userApi.getStudyRecords(userId, 20),
    ])
    analytics.value = analyticsRes
    studyRecords.value = recordsRes?.records || []
  } catch (err) {
    console.error('Analytics load failed:', err)
  } finally {
    loading.value = false
  }
})

const totalNodes = computed(() => analytics.value?.totalNodes || 0)
const masteredNodes = computed(() => analytics.value?.masteredNodes || 0)
const avgMastery = computed(() => analytics.value?.averageMastery || 0)

const categoryStats = computed(() => {
  const map = new Map<string, { total: number; mastered: number; sum: number }>()
  knowledgeStore.nodes.forEach(node => {
    if (node.category === 'Root' || node.category === 'Domain') return
    const cat = node.category || '其他'
    if (!map.has(cat)) map.set(cat, { total: 0, mastered: 0, sum: 0 })
    const stat = map.get(cat)!
    stat.total++
    const mastery = knowledgeStore.getNodeMastery(node.id)
    stat.sum += mastery
    if (mastery >= 90) stat.mastered++
  })
  return Array.from(map.entries()).map(([name, stat]) => ({
    name,
    total: stat.total,
    mastered: stat.mastered,
    avg: stat.total > 0 ? Math.round(stat.sum / stat.total) : 0,
  })).sort((a, b) => b.total - a.total)
})

const behaviorLabels: Record<string, string> = {
  read: '📖 阅读', learn: '📚 学习', practice: '✏️ 练习', review: '🔄 复习', debug: '🐛 调试'
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="analytics-view">
    <header class="view-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h1>学习分析</h1>
      </div>
    </header>

    <div v-if="loading" class="loading-state"><div class="spinner"></div><p>加载分析数据...</p></div>

    <div v-else class="analytics-content">
      <!-- Overview Cards -->
      <div class="stat-row">
        <div class="stat-card glass-card">
          <span class="stat-num">{{ totalNodes }}</span>
          <span class="stat-label">总知识点</span>
        </div>
        <div class="stat-card glass-card">
          <span class="stat-num mastered">{{ masteredNodes }}</span>
          <span class="stat-label">已掌握</span>
        </div>
        <div class="stat-card glass-card">
          <span class="stat-num">{{ avgMastery.toFixed(1) }}%</span>
          <span class="stat-label">平均掌握度</span>
        </div>
        <div class="stat-card glass-card">
          <span class="stat-num learning">{{ totalNodes - masteredNodes }}</span>
          <span class="stat-label">待学习</span>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div class="section-card glass-card">
        <h3>📊 分类掌握度分析</h3>
        <div class="category-list">
          <div v-for="cat in categoryStats" :key="cat.name" class="category-row">
            <div class="cat-info">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count">{{ cat.mastered }}/{{ cat.total }} 已掌握</span>
            </div>
            <div class="cat-bar">
              <div class="cat-bar-bg">
                <div class="cat-bar-fill" :style="{ width: cat.avg + '%' }"></div>
              </div>
              <span class="cat-percent">{{ cat.avg }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Knowledge Heatmap -->
      <div class="section-card glass-card">
        <h3>🗺️ 知识点掌握热力图</h3>
        <div class="heatmap">
          <div
            v-for="node in knowledgeStore.nodes.filter(n => n.category !== 'Root' && n.category !== 'Domain')"
            :key="node.id"
            class="heatmap-cell"
            :style="{ background: `hsl(${Math.round(knowledgeStore.getNodeMastery(node.id) * 1.2)}, 70%, ${90 - knowledgeStore.getNodeMastery(node.id) * 0.3}%)` }"
            :title="`${node.name}: ${knowledgeStore.getNodeMastery(node.id)}%`"
            @click="router.push({ path: '/map', query: { nodeId: node.id } })"
          >
            <span class="heatmap-label">{{ node.name.substring(0, 4) }}</span>
            <span class="heatmap-value">{{ knowledgeStore.getNodeMastery(node.id) }}%</span>
          </div>
        </div>
        <div class="heatmap-legend">
          <span>0%</span>
          <div class="legend-bar"></div>
          <span>100%</span>
        </div>
      </div>

      <!-- Recent Study Records -->
      <div class="section-card glass-card">
        <h3>📝 最近学习记录</h3>
        <div v-if="studyRecords.length === 0" class="empty-msg">暂无学习记录</div>
        <div v-else class="records-list">
          <div v-for="record in studyRecords" :key="record.id" class="record-item">
            <span class="record-behavior">{{ behaviorLabels[record.behavior] || record.behavior }}</span>
            <span class="record-node">{{ knowledgeStore.getNodeById(record.knowledgeNodeId)?.name || record.knowledgeNodeId }}</span>
            <span class="record-duration">{{ record.duration }}秒</span>
            <span class="record-time">{{ new Date(record.createdAt).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-view {
  width: 100vw; min-height: 100vh; background: var(--bg-primary); overflow-y: auto;
}

.view-header {
  position: sticky; top: 0; z-index: 20; padding: 16px 32px;
  background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0; }

.back-btn {
  background: transparent; border: 1px solid var(--border); border-radius: 8px;
  padding: 6px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; transition: all 0.2s;
}
.back-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; color: var(--text-secondary); }
.spinner { width: 32px; height: 32px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 12px; }
@keyframes spin { to { transform: rotate(360deg); } }

.analytics-content {
  max-width: 1100px; margin: 24px auto; padding: 0 24px;
  display: flex; flex-direction: column; gap: 20px;
}

.stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

.glass-card {
  background: rgba(255,255,255,0.7); border: 1px solid var(--border);
  border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.stat-card {
  padding: 20px; display: flex; flex-direction: column; align-items: center; text-align: center;
}
.stat-num { font-size: 28px; font-weight: 800; color: var(--text-primary); }
.stat-num.mastered { color: #10b981; }
.stat-num.learning { color: #3b82f6; }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }

.section-card { padding: 24px; }
.section-card h3 { font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0 0 16px; }

.category-list { display: flex; flex-direction: column; gap: 12px; }

.category-row { display: flex; flex-direction: column; gap: 4px; }
.cat-info { display: flex; justify-content: space-between; }
.cat-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.cat-count { font-size: 12px; color: var(--text-secondary); }
.cat-bar { display: flex; align-items: center; gap: 8px; }
.cat-bar-bg { flex: 1; height: 8px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden; }
.cat-bar-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 4px; transition: width 0.8s ease; }
.cat-percent { font-size: 13px; font-weight: 700; color: #6366f1; min-width: 40px; }

.heatmap {
  display: flex; flex-wrap: wrap; gap: 6px;
}
.heatmap-cell {
  width: 64px; height: 48px; border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.15s; border: 1px solid rgba(0,0,0,0.04);
}
.heatmap-cell:hover { transform: scale(1.08); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.heatmap-label { font-size: 10px; font-weight: 600; color: rgba(0,0,0,0.6); }
.heatmap-value { font-size: 11px; font-weight: 700; color: rgba(0,0,0,0.8); }

.heatmap-legend {
  display: flex; align-items: center; gap: 8px; margin-top: 12px;
  font-size: 11px; color: var(--text-secondary);
}
.legend-bar {
  flex: 1; height: 8px; border-radius: 4px;
  background: linear-gradient(90deg, hsl(0,70%,90%), hsl(60,70%,85%), hsl(120,70%,80%));
}

.empty-msg { text-align: center; color: var(--text-secondary); padding: 24px; }

.records-list { display: flex; flex-direction: column; gap: 6px; }
.record-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 8px; transition: background 0.15s;
}
.record-item:hover { background: var(--bg-secondary); }
.record-behavior { font-size: 13px; min-width: 80px; }
.record-node { flex: 1; font-size: 13px; font-weight: 500; color: var(--text-primary); }
.record-duration { font-size: 12px; color: var(--text-secondary); }
.record-time { font-size: 12px; color: var(--text-secondary); }

@media (max-width: 768px) { .stat-row { grid-template-columns: repeat(2, 1fr); } }
</style>
