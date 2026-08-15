<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  x: number
  y: number
  nodeId: string | null
}>()

const emit = defineEmits<{
  close: []
  action: [action: string, nodeId: string]
}>()

const menuRef = ref<HTMLDivElement>()

const actions = [
  { id: 'explain', label: 'AI解释', icon: '💡' },
  { id: 'practice', label: '生成练习', icon: '📝' },
  { id: 'plan', label: '加入学习计划', icon: '📋' },
  { id: 'errors', label: '查看错误记录', icon: '❌' }
]

const handleAction = (actionId: string) => {
  if (props.nodeId) {
    emit('action', actionId, props.nodeId)
  }
}

// 点击外部关闭菜单
const handleClickOutside = (event: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div 
    ref="menuRef"
    class="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 min-w-[160px]"
    :style="{ left: `${x}px`, top: `${y}px` }"
  >
    <button
      v-for="action in actions"
      :key="action.id"
      @click="handleAction(action.id)"
      class="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
    >
      <span class="mr-2">{{ action.icon }}</span>
      <span>{{ action.label }}</span>
    </button>
  </div>
</template>