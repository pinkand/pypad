import { ref, onMounted, onUnmounted } from 'vue'

export function usePerformance() {
  const fps = ref(0)
  const memoryUsage = ref(0)
  let frameCount = 0
  let lastTime = performance.now()
  let animationId: number

  // 计算FPS
  const calculateFPS = () => {
    frameCount++
    const currentTime = performance.now()
    
    if (currentTime - lastTime >= 1000) {
      fps.value = Math.round((frameCount * 1000) / (currentTime - lastTime))
      frameCount = 0
      lastTime = currentTime
    }
    
    animationId = requestAnimationFrame(calculateFPS)
  }

  // 获取内存使用情况
  const getMemoryUsage = () => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      memoryUsage.value = Math.round(memory.usedJSHeapSize / 1024 / 1024)
    }
  }

  // 节流函数
  const throttle = <T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): ((...args: Parameters<T>) => void) => {
    let inThrottle: boolean
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args)
        inThrottle = true
        setTimeout(() => (inThrottle = false), limit)
      }
    }
  }

  // 防抖函数
  const debounce = <T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): ((...args: Parameters<T>) => void) => {
    let timeout: ReturnType<typeof setTimeout>
    return (...args: Parameters<T>) => {
      clearTimeout(timeout)
      timeout = setTimeout(() => func(...args), wait)
    }
  }

  // 懒加载函数
  const lazyLoad = (callback: () => void, delay: number = 100) => {
    setTimeout(callback, delay)
  }

  onMounted(() => {
    calculateFPS()
    const memoryInterval = setInterval(getMemoryUsage, 5000)
    
    onUnmounted(() => {
      cancelAnimationFrame(animationId)
      clearInterval(memoryInterval)
    })
  })

  return {
    fps,
    memoryUsage,
    throttle,
    debounce,
    lazyLoad
  }
}