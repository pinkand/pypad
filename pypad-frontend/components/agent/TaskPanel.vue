<script setup lang="ts">
import { computed } from 'vue'
import { useAgentStore } from '@/stores/agent'
import type { Task } from '@/types/agent'

const agentStore = useAgentStore()

const tasksByStatus = computed(() => {
  return {
    pending: agentStore.pendingTasks,
    inProgress: agentStore.inProgressTasks,
    completed: agentStore.completedTasks
  }
})

const statusLabels = {
  pending: '待开始',
  in_progress: '进行中',
  completed: '已完成'
}

const statusColors = {
  pending: 'bg-white/80 text-gray-500 border border-black/5 shadow-sm',
  in_progress: 'bg-[#007aff] text-white shadow-sm',
  completed: 'bg-green-50 text-green-600 border border-green-100 shadow-sm'
}

const typeLabels = {
  learn: '学习',
  practice: '练习',
  debug: '调试',
  review: '复习'
}

const typeIcons = {
  learn: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>',
  practice: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>',
  debug: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20h9"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>',
  review: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>'
}

const updateTaskStatus = (taskId: string, status: Task['status']) => {
  agentStore.updateTaskStatus(taskId, status)
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- 头部 -->
    <div class="p-4 border-b border-black/5 bg-white/40 backdrop-blur-md">
      <h3 class="font-semibold text-gray-900">学习任务</h3>
      <p class="text-sm text-gray-500">
        {{ agentStore.pendingTasks.length }} 个待开始
      </p>
    </div>

    <!-- 任务列表 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-3">
      <!-- 进行中的任务 -->
      <div v-if="agentStore.inProgressTasks.length > 0">
        <h4 class="text-sm font-medium text-gray-500 mb-2 px-1">进行中</h4>
        <div 
          v-for="task in agentStore.inProgressTasks" 
          :key="task.id"
          class="p-4 bg-white/70 backdrop-blur-md rounded-xl border border-black/5 shadow-sm mb-3"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <span class="text-[#007aff] flex items-center" v-html="typeIcons[task.type]"></span>
              <span class="font-medium text-gray-900">{{ task.title }}</span>
            </div>
            <span :class="['px-2 py-1 text-xs rounded-full', statusColors[task.status]]">
              {{ statusLabels[task.status] }}
            </span>
          </div>
          <p class="text-sm text-gray-600 mb-3">{{ task.description }}</p>
          <div class="flex space-x-2">
            <button 
              @click="updateTaskStatus(task.id, 'completed')"
              class="px-3 py-1.5 text-xs bg-[#34c759] text-white rounded-lg hover:bg-green-600 transition-colors shadow-sm"
            >
              完成
            </button>
            <button 
              @click="updateTaskStatus(task.id, 'pending')"
              class="px-3 py-1.5 text-xs bg-white text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
            >
              暂停
            </button>
          </div>
        </div>
      </div>

      <!-- 待开始的任务 -->
      <div v-if="agentStore.pendingTasks.length > 0">
        <h4 class="text-sm font-medium text-gray-500 mb-2 px-1">待开始</h4>
        <div 
          v-for="task in agentStore.pendingTasks" 
          :key="task.id"
          class="p-4 bg-white/40 backdrop-blur-md rounded-xl border border-black/5 shadow-sm mb-3"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <span class="text-gray-400 flex items-center" v-html="typeIcons[task.type]"></span>
              <span class="font-medium text-gray-900">{{ task.title }}</span>
            </div>
            <span :class="['px-2 py-1 text-xs rounded-full', statusColors[task.status]]">
              {{ statusLabels[task.status] }}
            </span>
          </div>
          <p class="text-sm text-gray-600 mb-3">{{ task.description }}</p>
          <button 
            @click="updateTaskStatus(task.id, 'in_progress')"
            class="px-3 py-1.5 text-xs bg-[#007aff] text-white rounded-lg hover:bg-blue-600 transition-colors shadow-sm"
          >
            开始
          </button>
        </div>
      </div>

      <!-- 已完成的任务 -->
      <div v-if="agentStore.completedTasks.length > 0">
        <h4 class="text-sm font-medium text-gray-500 mb-2 px-1">已完成</h4>
        <div 
          v-for="task in agentStore.completedTasks.slice(0, 5)" 
          :key="task.id"
          class="p-4 bg-white/30 backdrop-blur-md rounded-xl border border-black/5 opacity-70 mb-3"
        >
          <div class="flex items-center justify-between mb-1">
            <div class="flex items-center space-x-2">
              <span class="text-[#34c759] flex items-center" v-html="typeIcons[task.type]"></span>
              <span class="font-medium text-gray-500 line-through">{{ task.title }}</span>
            </div>
            <span :class="['px-2 py-1 text-xs rounded-full', statusColors[task.status]]">
              {{ statusLabels[task.status] }}
            </span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="Object.values(tasksByStatus).every(tasks => tasks.length === 0)" class="text-center py-10">
        <div class="w-12 h-12 rounded-full bg-white/60 border border-black/5 shadow-sm flex items-center justify-center mx-auto mb-4 text-[#007aff]">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
        </div>
        <p class="text-gray-600 font-medium">暂无学习任务</p>
        <p class="text-sm text-gray-400 mt-1">
          AI会根据你的学习情况生成任务
        </p>
      </div>
    </div>
  </div>
</template>