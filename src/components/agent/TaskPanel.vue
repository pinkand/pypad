<script setup lang="ts">
import { computed } from 'vue'
import { useAgentStore } from '@/stores/agent'
import type { Task } from '@/types/agent'

const agentStore = useAgentStore()

const statusConfig = {
  pending:     { label: '待开始', class: 'badge-pending' },
  in_progress: { label: '进行中', class: 'badge-in-progress' },
  completed:   { label: '已完成', class: 'badge-completed' }
}

const typeConfig: Record<string, { icon: string; color: string }> = {
  learn:    { icon: '📚', color: '#818cf8' },
  practice: { icon: '💻', color: '#34d399' },
  debug:    { icon: '🐛', color: '#f87171' },
  review:   { icon: '🔄', color: '#fbbf24' }
}

const updateTaskStatus = (taskId: string, status: Task['status']) => {
  agentStore.updateTaskStatus(taskId, status)
}

const hasAnyTask = computed(() =>
  agentStore.inProgressTasks.length > 0 ||
  agentStore.pendingTasks.length > 0 ||
  agentStore.completedTasks.length > 0
)
</script>

<template>
  <div class="task-panel">
    <!-- Header -->
    <div class="panel-head">
      <div class="head-left">
        <span class="head-icon">📋</span>
        <h3 class="head-title">学习任务</h3>
      </div>
      <div class="task-counts">
        <span v-if="agentStore.inProgressTasks.length" class="count-badge count-progress">
          {{ agentStore.inProgressTasks.length }} 进行中
        </span>
        <span v-if="agentStore.pendingTasks.length" class="count-badge count-pending">
          {{ agentStore.pendingTasks.length }} 待开始
        </span>
      </div>
    </div>

    <!-- Task list -->
    <div class="task-list">
      <!-- In Progress -->
      <div v-if="agentStore.inProgressTasks.length > 0" class="task-section">
        <div class="section-label section-label--progress">
          <div class="section-dot pulse-dot" />
          进行中
        </div>
        <div
          v-for="task in agentStore.inProgressTasks"
          :key="task.id"
          class="task-card task-card--progress"
        >
          <div class="task-top">
            <div class="task-icon" :style="{ color: typeConfig[task.type]?.color }">
              {{ typeConfig[task.type]?.icon }}
            </div>
            <span class="task-title">{{ task.title }}</span>
            <span :class="['task-badge', statusConfig[task.status].class]">
              {{ statusConfig[task.status].label }}
            </span>
          </div>
          <p class="task-desc">{{ task.description }}</p>
          <div class="task-actions">
            <button class="task-btn task-btn--complete" @click="updateTaskStatus(task.id, 'completed')">
              ✓ 完成
            </button>
            <button class="task-btn task-btn--pause" @click="updateTaskStatus(task.id, 'pending')">
              ⏸ 暂停
            </button>
          </div>
        </div>
      </div>

      <!-- Pending -->
      <div v-if="agentStore.pendingTasks.length > 0" class="task-section">
        <div class="section-label section-label--pending">
          <div class="section-dot" style="background: #64748b;" />
          待开始
        </div>
        <div
          v-for="task in agentStore.pendingTasks"
          :key="task.id"
          class="task-card task-card--pending"
        >
          <div class="task-top">
            <div class="task-icon" :style="{ color: typeConfig[task.type]?.color }">
              {{ typeConfig[task.type]?.icon }}
            </div>
            <span class="task-title">{{ task.title }}</span>
            <span :class="['task-badge', statusConfig[task.status].class]">
              {{ statusConfig[task.status].label }}
            </span>
          </div>
          <p class="task-desc">{{ task.description }}</p>
          <button class="task-btn task-btn--start" @click="updateTaskStatus(task.id, 'in_progress')">
            ▶ 开始
          </button>
        </div>
      </div>

      <!-- Completed -->
      <div v-if="agentStore.completedTasks.length > 0" class="task-section">
        <div class="section-label section-label--done">
          <div class="section-dot" style="background: #10b981;" />
          已完成
        </div>
        <div
          v-for="task in agentStore.completedTasks.slice(0, 3)"
          :key="task.id"
          class="task-card task-card--done"
        >
          <div class="task-top">
            <div class="task-icon" style="opacity: 0.5;">{{ typeConfig[task.type]?.icon }}</div>
            <span class="task-title task-title--done">{{ task.title }}</span>
            <span :class="['task-badge', statusConfig[task.status].class]">
              {{ statusConfig[task.status].label }}
            </span>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-if="!hasAnyTask" class="task-empty">
        <div style="font-size: 28px; margin-bottom: 8px; opacity: 0.4;">📋</div>
        <p style="font-size: 13px; color: #475569;">暂无学习任务</p>
        <p style="font-size: 11px; color: #334155; margin-top: 4px;">AI 将根据学习情况自动生成</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* Header */
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(99, 102, 241, 0.12);
  flex-shrink: 0;
}

.head-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.head-icon { font-size: 16px; }

.head-title {
  font-size: 13px;
  font-weight: 700;
  color: #e2e8f0;
}

.task-counts {
  display: flex;
  gap: 6px;
}

.count-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 20px;
}

.count-progress {
  color: #818cf8;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.count-pending {
  color: #94a3b8;
  background: rgba(71, 85, 105, 0.2);
  border: 1px solid rgba(71, 85, 105, 0.3);
}

/* Task list */
.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 0 2px;
}

.section-label--progress { color: #818cf8; }
.section-label--pending  { color: #64748b; }
.section-label--done     { color: #34d399; }

.section-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.pulse-dot {
  background: #818cf8;
  animation: pulse-ring 2s ease-in-out infinite;
}

/* Task card */
.task-card {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color 0.2s ease;
}

.task-card--progress {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.25);
}

.task-card--pending {
  background: rgba(10, 22, 40, 0.4);
  border-color: rgba(71, 85, 105, 0.25);
}

.task-card--done {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.15);
  opacity: 0.65;
}

.task-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.task-title {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
  color: #e2e8f0;
  line-height: 1.3;
}

.task-title--done {
  text-decoration: line-through;
  color: #64748b;
}

.task-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 20px;
  border: 1px solid;
  flex-shrink: 0;
}

.task-desc {
  font-size: 11px;
  color: #475569;
  line-height: 1.4;
}

/* Buttons */
.task-actions {
  display: flex;
  gap: 6px;
}

.task-btn {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-btn--complete {
  color: #34d399;
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.35);
}

.task-btn--complete:hover {
  background: rgba(16, 185, 129, 0.2);
}

.task-btn--pause {
  color: #94a3b8;
  background: rgba(71, 85, 105, 0.15);
  border-color: rgba(71, 85, 105, 0.3);
}

.task-btn--pause:hover {
  background: rgba(71, 85, 105, 0.25);
}

.task-btn--start {
  color: #818cf8;
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.3);
}

.task-btn--start:hover {
  background: rgba(99, 102, 241, 0.22);
}

/* Empty */
.task-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 120px;
  text-align: center;
}
</style>