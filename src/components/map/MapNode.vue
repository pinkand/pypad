<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { MASTERY_COLORS, MASTERY_THRESHOLDS } from '@/utils/constants'

const props = defineProps<{
  data: {
    label: string
    description: string
    category: string
    importance: number
    mastery: number
  }
  selected?: boolean
}>()

const masteryColor = computed(() => {
  const mastery = props.data.mastery
  if (mastery >= MASTERY_THRESHOLDS.excellent) return MASTERY_COLORS.excellent
  if (mastery >= MASTERY_THRESHOLDS.good) return MASTERY_COLORS.good
  return MASTERY_COLORS.weak
})

const importanceSize = computed(() => {
  const base = 120
  const extra = props.data.importance * 10
  return Math.min(base + extra, 200)
})
</script>

<template>
  <div 
    :class="[
      'px-4 py-3 rounded-lg border-2 shadow-sm cursor-pointer transition-all duration-200',
      selected ? 'border-blue-500 shadow-md' : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
    ]"
    :style="{ 
      minWidth: `${importanceSize}px`,
      borderColor: selected ? '#3b82f6' : masteryColor + '40'
    }"
  >
    <!-- 输入连接点 -->
    <Handle type="target" :position="Position.Left" />

    <!-- 节点内容 -->
    <div class="flex flex-col">
      <div class="flex items-center justify-between mb-1">
        <h4 class="font-medium text-gray-900 dark:text-white text-sm">{{ data.label }}</h4>
        <span 
          class="px-1.5 py-0.5 text-xs font-medium rounded-full"
          :style="{ 
            backgroundColor: masteryColor + '20', 
            color: masteryColor 
          }"
        >
          {{ data.mastery }}%
        </span>
      </div>
      
      <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">
        {{ data.description }}
      </p>
      
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400 dark:text-gray-500">{{ data.category }}</span>
        <div class="flex space-x-1">
          <span 
            v-for="i in data.importance" 
            :key="i"
            class="w-1.5 h-1.5 rounded-full bg-yellow-400"
          ></span>
        </div>
      </div>
    </div>

    <!-- 输出连接点 -->
    <Handle type="source" :position="Position.Right" />
  </div>
</template>