<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { practiceApi } from '@/services/api'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useAppStore } from '@/stores/app'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()
const appStore = useAppStore()
const workspaceStore = useWorkspaceStore()
const loading = ref(true)
const practices = ref<any[]>([])
const selectedCategory = ref('all')

const categories = computed(() => {
  const cats = new Set(practices.value.map(p => {
    const node = knowledgeStore.getNodeById(p.knowledgeNodeId)
    return node?.category || '其他'
  }))
  return ['all', ...Array.from(cats)]
})

const filteredPractices = computed(() => {
  if (selectedCategory.value === 'all') return practices.value
  return practices.value.filter(p => {
    const node = knowledgeStore.getNodeById(p.knowledgeNodeId)
    return node?.category === selectedCategory.value
  })
})

onMounted(async () => {
  try {
    const res: any = await practiceApi.getPracticesByNode('')
    practices.value = res?.practices || []
  } catch (err) {
    console.error('Failed to load practices:', err)
  } finally {
    loading.value = false
  }
})

const startPractice = (practice: any) => {
  workspaceStore.currentCode = practice.starterCode || '# 在此编写代码\n'
  appStore.openWorkspace('practice')
}

const generatePractice = async (knowledgeId: string) => {
  try {
    const res: any = await practiceApi.generateAIPractice(knowledgeId, 'medium')
    if (res?.practice) {
      practices.value.push(res.practice)
    }
  } catch (err) {
    console.error('Generate practice failed:', err)
  }
}

const getDifficultyLabel = (d: string) => {
  const map: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
  return map[d] || d
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="practice-view">
    <header class="view-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h1>练习中心</h1>
      </div>
    </header>

    <div v-if="loading" class="loading-state"><div class="spinner"></div><p>加载练习题中...</p></div>

    <div v-else class="practice-content">
      <!-- Category Filter -->
      <div class="filter-bar">
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-btn"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          {{ cat === 'all' ? '全部' : cat }}
        </button>
      </div>

      <!-- Practice List -->
      <div class="practice-grid">
        <div
          v-for="p in filteredPractices"
          :key="p.id"
          class="practice-card glass-card"
          @click="startPractice(p)"
        >
          <div class="practice-header">
            <span class="practice-icon">✏️</span>
            <span class="difficulty-badge" :class="p.difficulty">{{ getDifficultyLabel(p.difficulty) }}</span>
          </div>
          <h3>{{ p.title }}</h3>
          <p class="practice-prompt">{{ p.prompt?.substring(0, 100) }}{{ p.prompt?.length > 100 ? '...' : '' }}</p>
          <div class="practice-meta">
            <span>{{ knowledgeStore.getNodeById(p.knowledgeNodeId)?.name || '通用' }}</span>
            <span class="type-tag">{{ p.type === 'ai_generated' ? 'AI 生成' : '预设' }}</span>
          </div>
        </div>
      </div>

      <div v-if="filteredPractices.length === 0" class="empty-state glass-card">
        <p>暂无练习题，可前往知识图谱选择知识点后生成</p>
        <button class="btn-secondary" @click="goToMap()">前往知识图谱</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.practice-view {
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

.practice-content {
  max-width: 1100px; margin: 24px auto; padding: 0 24px;
  display: flex; flex-direction: column; gap: 20px;
}

.filter-bar {
  display: flex; gap: 8px; flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 14px; border-radius: 99px; border: 1px solid var(--border);
  background: rgba(255,255,255,0.7); font-size: 13px; font-weight: 500;
  color: var(--text-secondary); cursor: pointer; transition: all 0.2s;
}
.filter-btn:hover { border-color: var(--accent); color: var(--accent); }
.filter-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }

.practice-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;
}

.glass-card {
  background: rgba(255,255,255,0.7); border: 1px solid var(--border);
  border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.practice-card {
  padding: 24px; cursor: pointer; transition: all 0.2s;
}
.practice-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }

.practice-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.practice-icon { font-size: 24px; }

.difficulty-badge {
  font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 99px;
}
.difficulty-badge.easy { background: rgba(16,185,129,0.1); color: #10b981; }
.difficulty-badge.medium { background: rgba(245,158,11,0.1); color: #f59e0b; }
.difficulty-badge.hard { background: rgba(239,68,68,0.1); color: #ef4444; }

.practice-card h3 { font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0 0 8px; }
.practice-prompt { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 12px; }

.practice-meta {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: var(--text-secondary);
}
.type-tag {
  font-size: 10px; padding: 2px 6px; border-radius: 99px;
  background: rgba(99,102,241,0.1); color: #6366f1;
}

.empty-state { padding: 48px; text-align: center; color: var(--text-secondary); display: flex; flex-direction: column; align-items: center; gap: 12px; }

.btn-secondary {
  padding: 8px 16px; border-radius: 99px; border: 1px solid var(--border);
  background: var(--bg-secondary); color: var(--text-primary); font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.btn-secondary:hover { background: var(--bg-tertiary); }
</style>
