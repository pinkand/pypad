<script setup lang="ts">
import { ref, shallowRef, computed, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'

const appStore = useAppStore()

const code = ref(`# 在这里编写Python代码\ndef hello():\n    print("Welcome to Python Learning OS!")\n\nhello()\n`)

const output = ref('')
const isRunning = ref(false)
const aiEvaluation = ref<{ type: 'success' | 'warning' | 'error' | 'info', message: string } | null>(null)

watch(() => appStore.workspaceMode, (newMode) => {
  output.value = ''
  aiEvaluation.value = null
  isRunning.value = false
  if (newMode === 'teach') {
    code.value = `# 教学示例：认识 Python 函数
def calculate_area(width, height):
    """计算矩形的面积"""
    return width * height

# 运行看看结果
area = calculate_area(5, 10)
print(f"矩形的面积是: {area}")
`
  } else if (newMode === 'practice') {
    code.value = `# 练习：实现一个计算阶乘的函数
# 要求：接收一个正整数 n，返回 n 的阶乘。
# 如果 n = 5，返回 120 (5 * 4 * 3 * 2 * 1)

def factorial(n):
    # TODO: 在此处编写你的代码
    pass
`
  } else {
    code.value = `# 自由编码区\ndef hello():\n    print("Welcome to Python Learning OS!")\n\nhello()\n`
  }
})

// Monaco Editor setup
const editorOptions = {
  theme: 'vs-light',
  automaticLayout: true,
  minimap: { enabled: false },
  fontSize: 14,
  fontFamily: 'JetBrains Mono, monospace',
  lineHeight: 24,
  padding: { top: 24 },
  scrollBeyondLastLine: false,
  roundedSelection: true,
  smoothScrolling: true,
  cursorBlinking: 'smooth',
  cursorSmoothCaretAnimation: 'on',
  formatOnPaste: true,
  scrollbar: {
    useShadows: false,
    verticalHasArrows: false,
    horizontalHasArrows: false,
    verticalScrollbarSize: 8,
    horizontalScrollbarSize: 8,
  }
}

const handleMount = (editor: any) => {
  // Can interact with monaco instance here
}

const runCode = async () => {
  isRunning.value = true
  output.value = ''
  aiEvaluation.value = null
  
  // Simulate execution
  setTimeout(() => {
    output.value = `> Executing...\nWelcome to Python Learning OS!\n> Done in 0.12s`
    aiEvaluation.value = {
      type: 'success',
      message: 'Excellent! The code is structurally sound and executes perfectly.'
    }
    isRunning.value = false
  }, 1000)
}

const debugCode = () => {
  output.value = '> Debugging session started...\nBreakpoint hit at line 2.'
}

const explainCode = () => {
  aiEvaluation.value = {
    type: 'info',
    message: 'This code defines a function `hello` that prints a greeting string to the standard output, and then calls the function.'
  }
}

const aiReview = () => {
  aiEvaluation.value = {
    type: 'warning',
    message: 'Consider adding type hints (e.g. `def hello() -> None:`) to improve code readability.'
  }
}

const submitCode = () => {
  isRunning.value = true
  output.value = ''
  aiEvaluation.value = null
  
  setTimeout(() => {
    output.value = `> Running Test Cases...\nTest 1 (n=5): Expected 120, Got None ❌\nTest 2 (n=1): Expected 1, Got None ❌`
    aiEvaluation.value = {
      type: 'error',
      message: '你的函数返回了 None。你需要使用 return 关键字返回计算结果。'
    }
    isRunning.value = false
  }, 1200)
}

const hintCode = () => {
  aiEvaluation.value = {
    type: 'info',
    message: '提示：你可以使用循环 (for/while) 或者递归来实现阶乘。'
  }
}
</script>

<template>
  <Transition name="workspace-fade">
    <div v-if="appStore.isWorkspaceOpen" class="workspace-overlay">
      <div class="workspace-container">
        
        <!-- Header -->
        <header class="workspace-header">
          <div class="header-left">
            <button class="icon-btn close-btn" @click="appStore.closeWorkspace()">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
            <div class="project-title">
              <span class="file-name">main.py</span>
              <span class="status-dot"></span>
            </div>
          </div>
          
          <div class="header-center">
            <div class="segmented-control">
              <button 
                class="seg-btn" 
                :class="{ active: appStore.workspaceMode === 'teach' }"
                @click="appStore.workspaceMode = 'teach'"
              >Teach</button>
              <button 
                class="seg-btn" 
                :class="{ active: appStore.workspaceMode === 'practice' }"
                @click="appStore.workspaceMode = 'practice'"
              >Practice</button>
              <button 
                class="seg-btn" 
                :class="{ active: appStore.workspaceMode === 'code' }"
                @click="appStore.workspaceMode = 'code'"
              >Code</button>
            </div>
          </div>
          
          <div class="header-right">
            <div class="user-avatar"></div>
          </div>
        </header>

        <!-- Main Content -->
        <div class="workspace-body">
          
          <!-- Left: Dynamic Panel based on Mode -->
          <aside class="left-panel glass-panel">
            
            <!-- TEACH MODE -->
            <div v-if="appStore.workspaceMode === 'teach'" class="panel-inner teach-panel">
              <div class="panel-header-small">
                <h3>AI 讲义</h3>
                <span class="badge info-badge">Learning</span>
              </div>
              <div class="teach-content">
                <h2>Python 函数基础</h2>
                <p>函数是组织好的，可重复使用的，用来实现单一，或相关联功能的代码段。</p>
                
                <h4>定义函数</h4>
                <p>你可以定义一个由自己想要功能的函数，以下是简单的规则：</p>
                <ul>
                  <li>函数代码块以 <code>def</code> 关键词开头，后接函数标识符名称和圆括号 <code>()</code>。</li>
                  <li>任何传入参数和自变量必须放在圆括号中间。</li>
                  <li>函数的第一行语句可以选择性地使用文档字符串—用于存放函数说明。</li>
                  <li>函数内容以冒号 <code>:</code> 起始，并且缩进。</li>
                </ul>
              </div>
            </div>

            <!-- PRACTICE MODE -->
            <div v-else-if="appStore.workspaceMode === 'practice'" class="panel-inner practice-panel">
              <div class="panel-header-small">
                <h3>实战练习</h3>
                <span class="badge warning-badge">Challenge</span>
              </div>
              <div class="practice-content">
                <h2>计算阶乘</h2>
                <p>编写一个函数 <code>factorial(n)</code>，接收一个正整数 <code>n</code>，返回 <code>n</code> 的阶乘。</p>
                
                <div class="test-cases">
                  <h4>测试用例</h4>
                  <div class="test-case">
                    <span class="test-label">输入: <code>5</code></span>
                    <span class="test-expected">预期输出: <code>120</code></span>
                  </div>
                  <div class="test-case">
                    <span class="test-label">输入: <code>1</code></span>
                    <span class="test-expected">预期输出: <code>1</code></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- CODE MODE (AI Tutor) -->
            <div v-else class="panel-inner ai-tutor-panel">
              <div class="panel-header-small">
                <h3>AI Tutor</h3>
                <span class="badge">Active</span>
              </div>
              
              <div class="tutor-section">
                <h4>Current Context</h4>
                <p class="tutor-text">Python Functions & Printing</p>
              </div>
              
              <div class="tutor-section">
                <h4>Suggestions</h4>
                <ul class="tutor-list">
                  <li>Try adding parameters to your function</li>
                  <li>Explore string formatting options</li>
                </ul>
              </div>
              
              <div class="tutor-section task-section">
                <h4>Next Task</h4>
                <div class="task-card">
                  <div class="task-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M22 4L12 14.01l-3-3" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                  <div class="task-details">
                    <h5>Create a greeting function</h5>
                    <p>Pass a name parameter to personalize it.</p>
                  </div>
                </div>
              </div>
            </div>
          </aside>

          <!-- Middle & Right: Editor and Output -->
          <main class="editor-main">
            
            <!-- Editor Area -->
            <div class="editor-container glass-panel">
              <div class="editor-toolbar">
                <div class="toolbar-actions">
                  <button class="action-btn run-btn" @click="runCode" :disabled="isRunning">
                    <svg v-if="!isRunning" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                    <svg v-else class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Run
                  </button>

                  <template v-if="appStore.workspaceMode === 'practice'">
                    <button class="action-btn submit-btn" @click="submitCode" :disabled="isRunning">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Submit
                    </button>
                    <div class="divider"></div>
                    <button class="action-btn ai-btn" @click="hintCode">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Hint
                    </button>
                  </template>

                  <template v-if="appStore.workspaceMode === 'code'">
                    <button class="action-btn" @click="debugCode">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 20a8 8 0 100-16 8 8 0 000 16zM12 14a2 2 0 100-4 2 2 0 000 4z"/>
                      </svg>
                      Debug
                    </button>
                    <div class="divider"></div>
                    <button class="action-btn ai-btn" @click="aiReview">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.792 0-5.484-.14-8.135-.411-1.718-.293-2.3-2.379-1.067-3.61l1.402-1.402M8.25 12h7.5" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Review
                    </button>
                  </template>
                  
                  <template v-if="appStore.workspaceMode !== 'practice'">
                    <button class="action-btn ai-btn" @click="explainCode">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Explain
                    </button>
                  </template>
                </div>
              </div>
              
              <div class="monaco-wrapper">
                <vue-monaco-editor
                  v-model:value="code"
                  theme="vs-light"
                  language="python"
                  :options="editorOptions"
                  @mount="handleMount"
                />
              </div>
            </div>

            <!-- Output Area -->
            <div class="output-container glass-panel">
              <div class="panel-header-small">
                <h3>Console</h3>
              </div>
              <div class="output-content">
                <!-- Standard Output -->
                <div class="terminal-output" v-if="output">
                  <pre>{{ output }}</pre>
                </div>
                
                <!-- AI Evaluation -->
                <Transition name="fade">
                  <div v-if="aiEvaluation" class="ai-evaluation" :class="aiEvaluation.type">
                    <div class="eval-header">
                      <svg v-if="aiEvaluation.type === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M22 4L12 14.01l-3-3" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <svg v-else-if="aiEvaluation.type === 'warning'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M12 16v-4m0-4h.01" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <span>AI Insights</span>
                    </div>
                    <p class="eval-message">{{ aiEvaluation.message }}</p>
                  </div>
                </Transition>
              </div>
            </div>

          </main>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Typography & Base */
.workspace-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(250, 250, 250, 0.4);
  backdrop-filter: blur(40px) saturate(150%);
  -webkit-backdrop-filter: blur(40px) saturate(150%);
}

.workspace-container {
  width: 96vw;
  height: 94vh;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255,255,255,0.4) inset;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.workspace-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.header-left, .header-right {
  flex: 1;
  display: flex;
  align-items: center;
}

.header-right {
  justify-content: flex-end;
}

.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
}

.project-title {
  margin-left: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--status-mastered);
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.segmented-control {
  display: flex;
  background: rgba(0, 0, 0, 0.04);
  padding: 4px;
  border-radius: 99px;
  gap: 4px;
}

.seg-btn {
  padding: 6px 16px;
  border: none;
  background: transparent;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.seg-btn:hover {
  color: var(--text-primary);
}

.seg-btn.active {
  background: #ffffff;
  color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  font-weight: 600;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  border: 1px solid rgba(255,255,255,0.6);
}

/* Body */
.workspace-body {
  flex: 1;
  display: flex;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(0, 0, 0, 0.04);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.left-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
}

.panel-inner {
  display: flex;
  flex-direction: column;
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.panel-header-small {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header-small h3 {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}

.badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 99px;
}

.badge:not(.info-badge):not(.warning-badge) {
  background: rgba(52, 199, 89, 0.1);
  color: var(--status-mastered);
}

.info-badge {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.warning-badge {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

/* Teach and Practice Content Styles */
.teach-content, .practice-content {
  color: var(--text-primary);
}

.teach-content h2, .practice-content h2 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
}

.teach-content p, .practice-content p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.teach-content h4, .practice-content h4 {
  font-size: 14px;
  font-weight: 600;
  margin-top: 20px;
  margin-bottom: 8px;
}

.teach-content ul {
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.teach-content ul li {
  margin-bottom: 8px;
}

.teach-content code, .practice-content code, .test-label code, .test-expected code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 12px;
}

.test-cases {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.test-case {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.04);
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}

.test-label {
  color: var(--text-primary);
  font-weight: 500;
}

.test-expected {
  color: var(--text-secondary);
}

/* AI Tutor Sidebar */
.tutor-section {
  margin-bottom: 24px;
}

.tutor-section h4 {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.tutor-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.tutor-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tutor-list li {
  font-size: 13px;
  color: var(--text-secondary);
  position: relative;
  padding-left: 12px;
}
.tutor-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-tertiary);
}

.task-card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.04);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.task-icon {
  color: var(--status-learning);
  margin-top: 2px;
}

.task-details h5 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.task-details p {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* Editor Main */
.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.editor-container {
  flex: 2;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-toolbar {
  padding: 12px 16px;
  display: flex;
  justify-content: flex-end;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.6);
  padding: 4px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.divider {
  width: 1px;
  height: 16px;
  background: rgba(0,0,0,0.1);
  margin: 0 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(0,0,0,0.04);
  color: var(--text-primary);
}

.run-btn {
  color: var(--status-mastered);
}
.run-btn:hover {
  background: rgba(52, 199, 89, 0.1);
}

.submit-btn {
  color: #ff9500;
}
.submit-btn:hover {
  background: rgba(255, 149, 0, 0.1);
}

.ai-btn {
  color: var(--status-learning);
}
.ai-btn:hover {
  background: rgba(0, 122, 255, 0.1);
}

.monaco-wrapper {
  flex: 1;
  width: 100%;
  position: relative;
}

/* Output Area */
.output-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

.output-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.terminal-output {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: #333;
  line-height: 1.5;
  border: 1px solid rgba(0,0,0,0.04);
}

.terminal-output pre {
  margin: 0;
}

.ai-evaluation {
  padding: 16px;
  border-radius: 12px;
  border: 1px solid;
  background: #ffffff;
}

.ai-evaluation.success {
  border-color: rgba(52, 199, 89, 0.3);
  background: rgba(52, 199, 89, 0.05);
}

.ai-evaluation.warning {
  border-color: rgba(255, 149, 0, 0.3);
  background: rgba(255, 149, 0, 0.05);
}

.ai-evaluation.info {
  border-color: rgba(0, 122, 255, 0.3);
  background: rgba(0, 122, 255, 0.05);
}

.eval-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
}

.success .eval-header { color: var(--status-mastered); }
.warning .eval-header { color: var(--status-weak); }
.info .eval-header { color: var(--status-learning); }

.eval-message {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
}

/* Transitions */
.workspace-fade-enter-active,
.workspace-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.workspace-fade-enter-from,
.workspace-fade-leave-to {
  opacity: 0;
  transform: scale(0.98) translateY(10px);
}
</style>
