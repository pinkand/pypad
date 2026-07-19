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
  const m = props.data.mastery
  if (m >= MASTERY_THRESHOLDS.excellent) return MASTERY_COLORS.excellent
  if (m >= MASTERY_THRESHOLDS.good) return MASTERY_COLORS.good
  return MASTERY_COLORS.weak
})

const importanceSize = computed(() => {
  const base = 130
  const extra = props.data.importance * 8
  return Math.min(base + extra, 200)
})

const masteryBarWidth = computed(() => `${Math.max(props.data.mastery, 4)}%`)
</script>

<template>
  <div
    class="map-node"
    :class="{ 'map-node--selected': selected }"
    :style="{
      minWidth: `${importanceSize}px`,
      '--node-color': masteryColor,
      '--node-glow': masteryColor + '44'
    }"
  >
    <!-- Connection handles -->
    <Handle type="target" :position="Position.Left" class="node-handle" />

    <!-- Node body -->
    <div class="node-body">
      <!-- Header row -->
      <div class="node-header">
        <h4 class="node-label">{{ data.label }}</h4>
        <span class="node-mastery" :style="{ color: masteryColor, background: masteryColor + '22' }">
          {{ data.mastery }}%
        </span>
      </div>

      <!-- Description -->
      <p class="node-desc">{{ data.description }}</p>

      <!-- Mastery progress bar -->
      <div class="node-progress">
        <div
          class="node-progress-fill"
          :style="{ width: masteryBarWidth, background: masteryColor }"
        />
      </div>

      <!-- Footer -->
      <div class="node-footer">
        <span class="node-category">{{ data.category }}</span>
        <div class="node-stars">
          <span
            v-for="i in Math.min(data.importance, 5)"
            :key="i"
            class="node-star"
          >★</span>
        </div>
      </div>
    </div>

    <!-- Selected glow ring -->
    <div v-if="selected" class="selected-ring" />

    <Handle type="source" :position="Position.Right" class="node-handle" />
  </div>
</template>

<style scoped>
.map-node {
  position: relative;
  background: rgba(10, 22, 40, 0.92);
  border: 1px solid var(--node-color, #6366f1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  overflow: hidden;
}

.map-node::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 10px;
  box-shadow: 0 0 12px var(--node-glow, rgba(99,102,241,0.3));
  opacity: 0.6;
  pointer-events: none;
  transition: opacity 0.25s ease;
}

.map-node:hover::before {
  opacity: 1;
}

.map-node:hover {
  transform: scale(1.03);
  box-shadow: 0 0 20px var(--node-glow, rgba(99,102,241,0.4));
}

.map-node--selected {
  border-color: #818cf8 !important;
  box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.3), 0 0 24px rgba(99, 102, 241, 0.4) !important;
}

/* Body */
.node-body {
  padding: 10px 12px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.node-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 6px;
}

.node-label {
  font-size: 12px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1.3;
  flex: 1;
}

.node-mastery {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 20px;
  flex-shrink: 0;
  letter-spacing: 0.3px;
}

.node-desc {
  font-size: 10px;
  color: #475569;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Progress bar */
.node-progress {
  height: 3px;
  background: rgba(30, 45, 74, 0.8);
  border-radius: 2px;
  overflow: hidden;
}

.node-progress-fill {
  height: 100%;
  border-radius: 2px;
  opacity: 0.85;
  min-width: 4px;
}

/* Footer */
.node-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.node-category {
  font-size: 9px;
  color: #334155;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.node-stars {
  display: flex;
  gap: 1px;
}

.node-star {
  font-size: 8px;
  color: #f59e0b;
  opacity: 0.75;
}

/* Selected ring animation */
.selected-ring {
  position: absolute;
  inset: -3px;
  border-radius: 13px;
  border: 1px solid rgba(129, 140, 248, 0.5);
  animation: glow-pulse 2s ease-in-out infinite;
  pointer-events: none;
}

/* Handle styles */
:deep(.node-handle) {
  width: 8px !important;
  height: 8px !important;
  background: var(--node-color, #6366f1) !important;
  border: 1.5px solid rgba(10, 22, 40, 0.8) !important;
}
</style>