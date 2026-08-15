<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { courseApi, chapterApi } from '@/services/api'

const router = useRouter()
const loading = ref(true)
const courses = ref<any[]>([])
const selectedCourse = ref<any>(null)
const chapters = ref<any[]>([])

onMounted(async () => {
  try {
    const res: any = await courseApi.getCourses()
    courses.value = res?.courses || []
    if (courses.value.length > 0) {
      selectCourse(courses.value[0])
    }
  } catch (err) {
    console.error('Failed to load courses:', err)
  } finally {
    loading.value = false
  }
})

const selectCourse = async (course: any) => {
  selectedCourse.value = course
  try {
    const res: any = await chapterApi.getChapters(course.id)
    chapters.value = res?.chapters || []
  } catch {
    chapters.value = []
  }
}

const goToMap = () => router.push('/map')
</script>

<template>
  <div class="courses-view">
    <header class="view-header">
      <div class="header-left">
        <button class="back-btn" @click="goToMap()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h1>课程中心</h1>
      </div>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载课程中...</p>
    </div>

    <div v-else class="courses-content">
      <!-- Course List -->
      <div class="course-grid">
        <div
          v-for="course in courses"
          :key="course.id"
          class="course-card glass-card"
          :class="{ active: selectedCourse?.id === course.id }"
          @click="selectCourse(course)"
        >
          <div class="course-icon">📘</div>
          <h3>{{ course.title }}</h3>
          <p>{{ course.description }}</p>
          <div class="course-meta">
            <span class="level-badge" :class="course.level">{{ course.level }}</span>
            <span class="category-tag">{{ course.category }}</span>
          </div>
        </div>
      </div>

      <!-- Chapters -->
      <div v-if="selectedCourse" class="chapters-section glass-card">
        <h2>📖 {{ selectedCourse.title }} — 章节目录</h2>
        <div v-if="chapters.length === 0" class="empty-msg">暂无章节数据</div>
        <div v-else class="chapter-list">
          <div v-for="(ch, idx) in chapters" :key="ch.id" class="chapter-item">
            <span class="chapter-num">{{ idx + 1 }}</span>
            <div class="chapter-info">
              <h4>{{ ch.title }}</h4>
              <p v-if="ch.description">{{ ch.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.courses-view {
  width: 100vw;
  min-height: 100vh;
  background: var(--bg-primary);
  overflow-y: auto;
}

.view-header {
  position: sticky;
  top: 0;
  z-index: 20;
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
.back-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: var(--text-secondary);
}

.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.courses-content {
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.glass-card {
  background: rgba(255,255,255,0.7);
  border: 1px solid var(--border);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.course-card {
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
}
.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}
.course-card.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(99,102,241,0.2);
}

.course-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.course-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.course-card p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 12px;
}

.course-meta {
  display: flex;
  gap: 8px;
}

.level-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 99px;
}
.level-badge.beginner { background: rgba(16,185,129,0.1); color: #10b981; }
.level-badge.intermediate { background: rgba(245,158,11,0.1); color: #f59e0b; }
.level-badge.advanced { background: rgba(239,68,68,0.1); color: #ef4444; }

.category-tag {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 99px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.chapters-section {
  padding: 24px;
}

.chapters-section h2 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.empty-msg {
  text-align: center;
  color: var(--text-secondary);
  padding: 24px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  transition: background 0.15s;
}
.chapter-item:hover { background: var(--bg-secondary); }

.chapter-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #6366f1;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chapter-info h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.chapter-info p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}
</style>
