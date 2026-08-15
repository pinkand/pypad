<script setup lang="ts">
import { ref, computed } from 'vue'
import type { VariablesMap, VariableInfo } from '@/types/knowledge'

const props = defineProps<{
  variables: VariablesMap | null
}>()

const expandedVars = ref<Set<string>>(new Set())

const variableList = computed(() => {
  if (!props.variables) return []
  return Object.entries(props.variables).map(([name, info]) => ({
    name,
    ...info
  }))
})

const toggleExpand = (name: string) => {
  if (expandedVars.value.has(name)) {
    expandedVars.value.delete(name)
  } else {
    expandedVars.value.add(name)
  }
}

const isExpandable = (info: VariableInfo): boolean => {
  return ['list', 'tuple', 'dict', 'set', 'frozenset'].includes(info.type) ||
    (typeof info.value === 'object' && info.value !== null)
}

const formatPreview = (info: VariableInfo): string => {
  if (info.type === 'NoneType') return 'None'
  if (info.type === 'str') return `"${String(info.value).substring(0, 60)}${String(info.value).length > 60 ? '...' : ''}"`
  if (info.type === 'bool') return info.value ? 'True' : 'False'
  if (['int', 'float', 'complex'].includes(info.type)) return String(info.value)
  if (info.type === 'bytes') return info.value
  if (['list', 'tuple', 'set', 'frozenset'].includes(info.type)) {
    return `${info.type}(${info.length ?? '?'} items)`
  }
  if (info.type === 'dict') {
    return `dict(${info.length ?? '?'} keys)`
  }
  if (typeof info.value === 'string') return info.value.substring(0, 80)
  return info.type
}

const getTypeColor = (type: string): string => {
  if (['int', 'float', 'complex', 'Decimal', 'Fraction'].includes(type)) return '#10b981'
  if (type === 'str') return '#f59e0b'
  if (type === 'bool') return '#8b5cf6'
  if (['list', 'tuple', 'set', 'frozenset'].includes(type)) return '#3b82f6'
  if (type === 'dict') return '#ec4899'
  if (type === 'NoneType') return '#9ca3af'
  return '#6366f1'
}

const renderObjectEntries = (value: any): Array<{ key: string; info: VariableInfo }> => {
  if (!value || typeof value !== 'object') return []
  return Object.entries(value).map(([k, v]) => ({
    key: k,
    info: v as VariableInfo
  }))
}

const renderListItems = (value: any): VariableInfo[] => {
  if (!Array.isArray(value)) return []
  return value as VariableInfo[]
}
</script>

<template>
  <div class="variable-inspector">
    <div class="inspector-header">
      <div class="header-left">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>变量监视</span>
      </div>
      <span class="var-count">{{ variableList.length }} 个变量</span>
    </div>

    <div v-if="!variables || variableList.length === 0" class="empty-state">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 16v-4m0-4h.01" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p>运行代码后查看变量状态</p>
    </div>

    <div v-else class="var-list">
      <div
        v-for="v in variableList"
        :key="v.name"
        class="var-item"
        :class="{ expandable: isExpandable(v), expanded: expandedVars.has(v.name) }"
      >
        <div class="var-row" @click="isExpandable(v) && toggleExpand(v.name)">
          <div class="var-info">
            <span v-if="isExpandable(v)" class="expand-icon">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" v-if="!expandedVars.has(v.name)"/>
                <path d="M5 8l14 0" stroke="currentColor" stroke-width="2" v-else/>
              </svg>
            </span>
            <span v-else class="expand-placeholder"></span>
            <span class="var-name">{{ v.name }}</span>
            <span class="var-type" :style="{ color: getTypeColor(v.type) }">{{ v.type }}</span>
          </div>
          <span class="var-preview">{{ formatPreview(v) }}</span>
        </div>

        <!-- Expanded: dict/object -->
        <div v-if="expandedVars.has(v.name) && v.type === 'dict' && typeof v.value === 'object' && v.value !== null" class="var-children">
          <div v-for="entry in renderObjectEntries(v.value)" :key="entry.key" class="var-child">
            <span class="child-key">{{ entry.key }}:</span>
            <span class="child-type" :style="{ color: getTypeColor(entry.info.type) }">{{ entry.info.type }}</span>
            <span class="child-preview">{{ formatPreview(entry.info) }}</span>
          </div>
        </div>

        <!-- Expanded: list/tuple/set -->
        <div v-else-if="expandedVars.has(v.name) && Array.isArray(v.value)" class="var-children">
          <div v-for="(item, idx) in renderListItems(v.value)" :key="idx" class="var-child">
            <span class="child-key">[{{ idx }}]:</span>
            <span class="child-type" :style="{ color: getTypeColor(item.type) }">{{ item.type }}</span>
            <span class="child-preview">{{ formatPreview(item) }}</span>
          </div>
        </div>

        <!-- Expanded: object with __dict__ -->
        <div v-else-if="expandedVars.has(v.name) && typeof v.value === 'object' && v.value !== null && !Array.isArray(v.value)" class="var-children">
          <div v-for="entry in renderObjectEntries(v.value)" :key="entry.key" class="var-child">
            <span class="child-key">{{ entry.key }}:</span>
            <span class="child-type" :style="{ color: getTypeColor(entry.info.type) }">{{ entry.info.type }}</span>
            <span class="child-preview">{{ formatPreview(entry.info) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.variable-inspector {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.inspector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 0 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  margin-bottom: 12px;
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

.var-count {
  font-size: 11px;
  color: var(--text-tertiary);
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 8px;
  border-radius: 99px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--text-tertiary);
  gap: 8px;
  padding: 24px 0;
}

.empty-state p {
  font-size: 12px;
  margin: 0;
}

.var-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.var-item {
  border-radius: 6px;
  transition: background 0.15s;
}

.var-item.expandable {
  cursor: pointer;
}

.var-item.expandable:hover {
  background: rgba(0, 0, 0, 0.03);
}

.var-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 6px;
  gap: 8px;
}

.var-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  flex-shrink: 0;
}

.expand-icon {
  display: flex;
  align-items: center;
  color: var(--text-tertiary);
  width: 12px;
  flex-shrink: 0;
}

.expand-placeholder {
  width: 12px;
  flex-shrink: 0;
}

.var-name {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.var-type {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.04);
  white-space: nowrap;
}

.var-preview {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 11px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: right;
  min-width: 0;
}

.var-children {
  padding: 2px 0 4px 30px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.var-child {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 6px;
  font-size: 11px;
}

.child-key {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  color: var(--text-tertiary);
  flex-shrink: 0;
  min-width: 40px;
}

.child-type {
  font-size: 9px;
  font-weight: 500;
  padding: 0px 4px;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.03);
  flex-shrink: 0;
}

.child-preview {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
</style>
