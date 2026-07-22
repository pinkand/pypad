<script setup lang="ts">
import { computed } from 'vue'
import { getBezierPath } from '@vue-flow/core'

const props = defineProps({
  id: String,
  source: String,
  target: String,
  sourceX: { type: Number, required: true },
  sourceY: { type: Number, required: true },
  targetX: { type: Number, required: true },
  targetY: { type: Number, required: true },
  sourcePosition: { type: String as any, required: true },
  targetPosition: { type: String as any, required: true },
  data: Object,
  markerEnd: String,
  style: Object
})

const path = computed(() => {
  return getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    targetX: props.targetX,
    targetY: props.targetY,
    sourcePosition: props.sourcePosition,
    targetPosition: props.targetPosition
  })
})

const edgeColor = computed(() => {
  if (props.data?.relationType === 'prerequisite') return '#3b82f6'
  if (props.data?.relationType === 'extends') return '#8b5cf6'
  return '#6b7280'
})
</script>

<template>
  <path
    :d="path[0]"
    :style="{ stroke: edgeColor, strokeWidth: 2 }"
    fill="none"
    :stroke-dasharray="data?.strength === 'soft' ? '5,5' : 'none'"
  />
</template>