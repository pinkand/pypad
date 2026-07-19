<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAgentStore } from '@/stores/agent'

const agentStore = useAgentStore()

const code = ref(`# 在这里编写 Python 代码
def hello():
    print("Hello, Python Learning OS!")

hello()
`)

const output = ref('')
const isRunning = ref(false)

// Simulate run
const runCode = async () => {
  isRunning.value = true
  output.value = ''

  setTimeout(() => {
    output.value = `>>> 执行代码...
Hello, Python Learning OS!
>>> 执行完成 ✓`
    isRunning.value = false
    agentStore.addMessage('system', '代码执行成功')
  }, 1200)
}

// Analyze code
const analyzeCode = () => {
  agentStore.addMessage('user', `请分析这段代码：\n\`\`\`python\n${code.value}\n\`\`\``)
  setTimeout(() => {
    agentStore.addMessage('assistant', '这段代码定义了一个简单的函数并调用它。代码结构清晰，符合 Python 最佳实践。')
  }, 500)
}

const clearCode = () => {
  code.value = ''
  output.value = ''
}

const lineCount = computed(() => code.value.split('\n').length)
</script>

<template>
  <div class="code-editor">
    <!-- Header -->
    <div class="editor-header">
      <div class="editor-title-row">
        <div class="editor-dot red" />
        <div class="editor-dot yellow" />
        <div class="editor-dot green" />
        <span class="editor-filename">main.py</span>
        <span class="line-count">{{ lineCount }} 行</span>
      </div>
      <div class="editor-actions">
        <button class="editor-btn editor-btn--ai" @click="analyzeCode" title="AI 分析代码">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          AI 分析
        </button>
        <button class="editor-btn editor-btn--clear" @click="clearCode" title="清空代码">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Code area -->
    <div class="code-area">
      <!-- Line numbers -->
      <div class="line-numbers" aria-hidden="true">
        <div
          v-for="n in lineCount"
          :key="n"
          class="line-num"
        >{{ n }}</div>
      </div>
      <!-- Textarea -->
      <textarea
        v-model="code"
        class="code-input"
        spellcheck="false"
        placeholder="# 在这里编写 Python 代码..."
      />
    </div>

    <!-- Run button -->
    <div class="run-row">
      <button
        class="run-btn"
        @click="runCode"
        :disabled="isRunning"
        :class="{ 'run-btn--running': isRunning }"
      >
        <svg v-if="isRunning" class="spin-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ isRunning ? '运行中...' : '▶  运行' }}
      </button>
    </div>

    <!-- Output -->
    <div class="output-area">
      <div class="output-header">
        <span class="output-label">输出</span>
        <button v-if="output" class="output-clear" @click="output = ''">清空</button>
      </div>
      <pre class="output-content">{{ output || '等待运行...' }}</pre>
    </div>
  </div>
</template>

<style scoped>
.code-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #020817;
}

/* Editor header (traffic lights style) */
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(10, 22, 40, 0.9);
  border-bottom: 1px solid rgba(99, 102, 241, 0.12);
  flex-shrink: 0;
}

.editor-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.editor-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.editor-dot.red    { background: #ff5f57; }
.editor-dot.yellow { background: #febc2e; }
.editor-dot.green  { background: #28c840; }

.editor-filename {
  font-size: 12px;
  color: #64748b;
  margin-left: 6px;
  font-family: 'JetBrains Mono', monospace;
}

.line-count {
  font-size: 10px;
  color: #334155;
  font-family: 'JetBrains Mono', monospace;
}

.editor-actions {
  display: flex;
  gap: 6px;
}

.editor-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
}

.editor-btn--ai {
  color: #818cf8;
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
}

.editor-btn--ai:hover {
  background: rgba(99, 102, 241, 0.2);
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
}

.editor-btn--clear {
  color: #64748b;
  background: transparent;
  border-color: rgba(71, 85, 105, 0.3);
  width: 26px;
  height: 26px;
  padding: 0;
  justify-content: center;
}

.editor-btn--clear:hover {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
}

/* Code area */
.code-area {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.line-numbers {
  padding: 10px 8px 10px 12px;
  background: rgba(5, 10, 24, 0.6);
  border-right: 1px solid rgba(99, 102, 241, 0.08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.line-num {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: #1e3a5f;
  line-height: 1.6;
  user-select: none;
  text-align: right;
  min-width: 20px;
}

.code-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #7dd3fc;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  padding: 10px 12px;
  resize: none;
  overflow-y: auto;
}

.code-input::placeholder {
  color: #1e3a5f;
}

/* Run button */
.run-row {
  padding: 8px 12px;
  flex-shrink: 0;
  background: rgba(5, 10, 24, 0.6);
}

.run-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px;
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.5px;
}

.run-btn:not(:disabled):hover {
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
  filter: brightness(1.1);
}

.run-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  animation: orbit 1s linear infinite;
}

/* Output */
.output-area {
  flex-shrink: 0;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
  background: rgba(2, 8, 23, 0.9);
  max-height: 120px;
  display: flex;
  flex-direction: column;
}

.output-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px 4px;
  border-bottom: 1px solid rgba(99, 102, 241, 0.08);
}

.output-label {
  font-size: 10px;
  font-weight: 700;
  color: #334155;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
}

.output-clear {
  font-size: 10px;
  color: #334155;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.output-clear:hover { color: #64748b; }

.output-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #34d399;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>