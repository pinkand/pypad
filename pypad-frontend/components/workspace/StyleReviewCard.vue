<script setup lang="ts">
import { computed } from 'vue'
import type { StyleReview, StyleIssue } from '@/types/knowledge'

const props = defineProps<{
  review: StyleReview | null
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'goto-line', line: number): void
}>()

const scoreColor = computed(() => {
  if (!props.review) return '#9ca3af'
  if (props.review.score >= 90) return '#10b981'
  if (props.review.score >= 70) return '#f59e0b'
  return '#ef4444'
})

const categoryLabel = computed(() => {
  if (!props.review) return ''
  const map: Record<string, string> = {
    excellent: '优秀',
    good: '良好',
    fair: '一般',
    needs_improvement: '需改进',
    error: '错误'
  }
  return map[props.review.category] || props.review.category
})

const severityIcon = (severity: string): string => {
  switch (severity) {
    case 'high': return '🔴'
    case 'medium': return '🟡'
    case 'low': return '🔵'
    default: return '💡'
  }
}

const ruleLabels: Record<string, string> = {
  'use-list-comprehension': '列表推导式',
  'use-isinstance': 'isinstance',
  'no-bare-except': '异常处理',
  'simplify-bool-compare': '布尔简化',
  'use-join': '字符串拼接',
  'use-with-open': '文件操作',
  'use-truthiness': '真值判断',
}

const getRuleLabel = (rule: string): string => {
  return ruleLabels[rule] || rule
}
</script>

<template>
  <div class="style-review-card">
    <div class="card-header">
      <div class="header-left">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>Pythonic 风格分析</span>
      </div>
      <span v-if="review" class="category-badge" :class="review.category">
        {{ categoryLabel }}
      </span>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="mini-spinner"></div>
      <span>分析中...</span>
    </div>

    <div v-else-if="!review" class="empty-state">
      <p>运行代码后点击 Review 获取风格分析</p>
    </div>

    <template v-else>
      <!-- Score Bar -->
      <div class="score-section">
        <div class="score-circle" :style="{ borderColor: scoreColor }">
          <span class="score-value" :style="{ color: scoreColor }">{{ review.score }}</span>
          <span class="score-label">/100</span>
        </div>
        <div class="score-meta">
          <span class="issue-count">{{ review.issues.length }} 个问题</span>
          <div class="score-bar-bg">
            <div class="score-bar-fill" :style="{ width: review.score + '%', background: scoreColor }"></div>
          </div>
        </div>
      </div>

      <!-- Suggestions -->
      <div v-if="review.suggestions.length > 0" class="suggestions-section">
        <h4>改进建议</h4>
        <div class="suggestion-list">
          <div v-for="(s, idx) in review.suggestions" :key="idx" class="suggestion-item">
            <span class="suggestion-bullet">→</span>
            <span>{{ s }}</span>
          </div>
        </div>
      </div>

      <!-- Issues List -->
      <div v-if="review.issues.length > 0" class="issues-section">
        <h4>问题详情</h4>
        <div class="issue-list">
          <div
            v-for="(issue, idx) in review.issues"
            :key="idx"
            class="issue-item"
            :class="issue.severity"
            @click="emit('goto-line', issue.line)"
          >
            <div class="issue-header">
              <span class="issue-severity">{{ severityIcon(issue.severity) }}</span>
              <span class="issue-rule">{{ getRuleLabel(issue.rule) }}</span>
              <span class="issue-line" @click.stop="emit('goto-line', issue.line)">L{{ issue.line }}</span>
            </div>
            <p class="issue-message">{{ issue.message }}</p>
            <p v-if="issue.example" class="issue-example">
              <code>{{ issue.example }}</code>
            </p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.style-review-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}

.category-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 99px;
}

.category-badge.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.category-badge.good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.category-badge.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.category-badge.needs_improvement {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-tertiary);
  font-size: 12px;
  padding: 16px 0;
}

.mini-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--accent, #6366f1);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  color: var(--text-tertiary);
  font-size: 12px;
  text-align: center;
  padding: 16px 0;
}

.empty-state p { margin: 0; }

.score-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 3px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.score-value {
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
}

.score-label {
  font-size: 9px;
  color: var(--text-tertiary);
}

.score-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.issue-count {
  font-size: 11px;
  color: var(--text-secondary);
}

.score-bar-bg {
  height: 4px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.suggestions-section h4,
.issues-section h4 {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin: 0 0 8px;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: var(--text-primary);
  line-height: 1.4;
}

.suggestion-bullet {
  color: var(--accent, #6366f1);
  font-weight: 700;
  flex-shrink: 0;
}

.issue-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 240px;
  overflow-y: auto;
}

.issue-item {
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.04);
  cursor: default;
  transition: background 0.15s;
}

.issue-item.high {
  border-left: 3px solid #ef4444;
}

.issue-item.medium {
  border-left: 3px solid #f59e0b;
}

.issue-item.low {
  border-left: 3px solid #3b82f6;
}

.issue-item.info {
  border-left: 3px solid #6366f1;
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.issue-severity {
  font-size: 10px;
}

.issue-rule {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.04);
  padding: 1px 5px;
  border-radius: 3px;
}

.issue-line {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 10px;
  color: var(--accent, #6366f1);
  cursor: pointer;
  margin-left: auto;
  padding: 1px 4px;
  border-radius: 3px;
  transition: background 0.15s;
}

.issue-line:hover {
  background: rgba(99, 102, 241, 0.1);
}

.issue-message {
  font-size: 12px;
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0;
}

.issue-example {
  margin: 4px 0 0;
}

.issue-example code {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 11px;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 5px;
  border-radius: 3px;
}
</style>
