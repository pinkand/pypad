<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { projectApi } from '@/services/api'
import { useAppStore } from '@/stores/app'
import { useWorkspaceStore } from '@/stores/workspace'

const router = useRouter()
const appStore = useAppStore()
const workspaceStore = useWorkspaceStore()
const loading = ref(true)
const projects = ref<any[]>([])
const selectedProject = ref<any>(null)

onMounted(async () => {
  try {
    const res: any = await projectApi.getProjects()
    projects.value = res?.projects || []
  } catch (err) {
    console.error('Failed to load projects:', err)
  } finally {
    loading.value = false
  }
})

const selectProject = async (id: string) => {
  try {
    const res: any = await projectApi.getProject(id)
    selectedProject.value = res?.project || res
  } catch {
    selectedProject.value = null
  }
}

const startProject = () => {
  if (selectedProject.value?.initCode) {
    workspaceStore.currentCode = selectedProject.value.initCode
    appStore.openWorkspace('code')
  }
}

const getDifficultyLabel = (d: string) => {
  const map: Record<string, string> = { easy: '入门', medium: '进阶', hard: '高级' }
  return map[d] || d
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="projects-view">
    <header class="view-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h1>项目实战</h1>
      </div>
    </header>

    <div v-if="loading" class="loading-state"><div class="spinner"></div><p>加载项目中...</p></div>

    <div v-else class="projects-content">
      <!-- Project List -->
      <div class="project-grid">
        <div
          v-for="p in projects"
          :key="p.id"
          class="project-card glass-card"
          :class="{ active: selectedProject?.id === p.id }"
          @click="selectProject(p.id)"
        >
          <div class="project-header">
            <span class="project-icon">🚀</span>
            <span class="difficulty-badge" :class="p.difficulty">{{ getDifficultyLabel(p.difficulty) }}</span>
          </div>
          <h3>{{ p.title }}</h3>
          <p>{{ p.description }}</p>
          <div class="project-meta">
            <span v-if="p.estimatedHours">⏱ {{ p.estimatedHours }}h</span>
          </div>
        </div>
      </div>

      <div v-if="projects.length === 0" class="empty-state glass-card">
        <p>暂无项目数据</p>
      </div>

      <!-- Project Detail -->
      <div v-if="selectedProject" class="project-detail glass-card">
        <h2>{{ selectedProject.title }}</h2>
        <p class="detail-desc">{{ selectedProject.description }}</p>

        <div v-if="selectedProject.readmeMarkdown" class="readme-section">
          <h3>📖 项目说明</h3>
          <pre class="readme-content">{{ selectedProject.readmeMarkdown }}</pre>
        </div>

        <div class="detail-actions">
          <button class="btn-primary" @click="startProject">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            开始项目
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects-view {
  width: 100vw;
  min-height: 100vh;
  background: var(--bg-primary);
  overflow-y: auto;
}

.view-header {
  position: sticky; top: 0; z-index: 20;
  padding: 16px 32px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
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

.projects-content {
  max-width: 1100px; margin: 24px auto; padding: 0 24px;
  display: flex; flex-direction: column; gap: 24px;
}

.project-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;
}

.glass-card {
  background: rgba(255,255,255,0.7); border: 1px solid var(--border);
  border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.project-card {
  padding: 24px; cursor: pointer; transition: all 0.2s;
}
.project-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.project-card.active { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(99,102,241,0.2); }

.project-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.project-icon { font-size: 28px; }

.difficulty-badge {
  font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 99px;
}
.difficulty-badge.easy { background: rgba(16,185,129,0.1); color: #10b981; }
.difficulty-badge.medium { background: rgba(245,158,11,0.1); color: #f59e0b; }
.difficulty-badge.hard { background: rgba(239,68,68,0.1); color: #ef4444; }

.project-card h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin: 0 0 8px; }
.project-card p { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 12px; }
.project-meta { font-size: 12px; color: var(--text-secondary); }

.empty-state { padding: 48px; text-align: center; color: var(--text-secondary); }

.project-detail { padding: 24px; }
.project-detail h2 { font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 0 0 8px; }
.detail-desc { font-size: 14px; color: var(--text-secondary); margin: 0 0 20px; }

.readme-section { margin-bottom: 20px; }
.readme-section h3 { font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px; }
.readme-content {
  background: #f8f9fa; border-radius: 8px; padding: 16px;
  font-family: monospace; font-size: 13px; line-height: 1.6;
  white-space: pre-wrap; max-height: 300px; overflow-y: auto;
}

.detail-actions { display: flex; gap: 12px; }

.btn-primary {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px; border-radius: 99px;
  background: var(--accent); color: #fff; border: none;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
</style>
