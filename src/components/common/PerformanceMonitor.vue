<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { usePerformance } from '@/composables/usePerformance'

const { fps, memoryUsage } = usePerformance()
const isVisible = ref(false)

// 切换显示
const toggleVisibility = () => {
  isVisible.value = !isVisible.value
}

// 键盘快捷键
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'p' && event.ctrlKey) {
    event.preventDefault()
    toggleVisibility()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div 
    v-if="isVisible"
    class="fixed bottom-4 right-4 z-50 bg-black/80 text-white p-3 rounded-lg font-mono text-xs"
  >
    <div class="flex items-center space-x-4">
      <div>
        <span class="text-gray-400">FPS:</span>
        <span :class="{ 'text-red-400': fps < 30, 'text-yellow-400': fps >= 30 && fps < 60, 'text-green-400': fps >= 60 }">
          {{ fps }}
        </span>
      </div>
      <div>
        <span class="text-gray-400">内存:</span>
        <span>{{ memoryUsage }}MB</span>
      </div>
      <button 
        @click="isVisible = false"
        class="text-gray-400 hover:text-white ml-2"
      >
        ×
      </button>
    </div>
  </div>
  
  <!-- 触发按钮 -->
  <button 
    v-if="!isVisible"
    @click="toggleVisibility"
    class="fixed bottom-4 right-4 z-50 w-8 h-8 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors"
    title="性能监控 (Ctrl+P)"
  >
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  </button>
</template>