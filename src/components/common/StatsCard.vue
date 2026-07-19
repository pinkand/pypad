<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  title: string
  value: number | string
  icon: string
  color: 'blue' | 'green' | 'yellow' | 'red'
}>()

const colorMap = {
  blue:   { primary: '#6366f1', glow: 'rgba(99,102,241,0.25)',  bg: 'rgba(99,102,241,0.12)'  },
  green:  { primary: '#10b981', glow: 'rgba(16,185,129,0.25)',  bg: 'rgba(16,185,129,0.12)'  },
  yellow: { primary: '#f59e0b', glow: 'rgba(245,158,11,0.25)',  bg: 'rgba(245,158,11,0.12)'  },
  red:    { primary: '#ef4444', glow: 'rgba(239,68,68,0.25)',   bg: 'rgba(239,68,68,0.12)'   }
}

const colors = colorMap[props.color]

// Animated counter
const displayValue = ref(0)

onMounted(() => {
  const target = typeof props.value === 'number' ? props.value : 0
  if (target === 0) { displayValue.value = 0; return }
  const duration = 900
  const start = Date.now()
  const tick = () => {
    const elapsed = Date.now() - start
    const progress = Math.min(elapsed / duration, 1)
    const ease = 1 - Math.pow(1 - progress, 3)
    displayValue.value = Math.round(ease * target)
    if (progress < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
})
</script>

<template>
  <div class="stats-card animate-slide-up" :style="{ '--card-color': colors.primary }">
    <div class="card-inner">
      <!-- Icon -->
      <div class="card-icon" :style="{ background: colors.bg, boxShadow: `0 0 16px ${colors.glow}` }">
        <span class="card-emoji">{{ icon }}</span>
      </div>

      <!-- Info -->
      <div class="card-body">
        <p class="card-title">{{ title }}</p>
        <div class="card-value">
          <span v-if="typeof value === 'number'">{{ displayValue }}</span>
          <span v-else>{{ value }}</span>
        </div>
      </div>

      <!-- Decorative line -->
      <div class="card-line" :style="{ background: `linear-gradient(180deg, ${colors.primary}, transparent)` }" />
    </div>
  </div>
</template>

<style scoped>
.stats-card {
  position: relative;
  border-radius: 14px;
  background: rgba(15, 31, 56, 0.65);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(99, 102, 241, 0.15);
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.25s ease;
  overflow: hidden;
  cursor: default;
}

.stats-card:hover {
  border-color: var(--card-color);
  box-shadow: 0 0 24px color-mix(in srgb, var(--card-color) 20%, transparent),
              0 8px 32px rgba(0, 0, 0, 0.4);
  transform: translateY(-3px);
}

.card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  position: relative;
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.25s ease;
}

.stats-card:hover .card-icon {
  transform: scale(1.1) rotate(-5deg);
}

.card-emoji {
  font-size: 22px;
  line-height: 1;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 4px;
}

.card-value {
  font-size: 28px;
  font-weight: 800;
  color: #f1f5f9;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

/* Right accent bar */
.card-line {
  position: absolute;
  right: 0;
  top: 0;
  width: 3px;
  height: 100%;
  opacity: 0.6;
}
</style>