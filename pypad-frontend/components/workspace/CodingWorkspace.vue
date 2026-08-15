<script setup lang="ts">
import { ref, shallowRef, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useWorkspaceStore } from '@/stores/workspace'
import { useKnowledgeStore } from '@/stores/knowledge'
import { usePracticeStore } from '@/stores/practice'
import { useSessionStore } from '@/stores/session'
import { agentApi, workspaceApi, practiceApi } from '@/services/api'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'

const appStore = useAppStore()
const workspaceStore = useWorkspaceStore()
const knowledgeStore = useKnowledgeStore()
const practiceStore = usePracticeStore()
const sessionStore = useSessionStore()

const code = ref(`# 在这里编写Python代码\ndef hello():\n    print("Welcome to PyPad!")\n\nhello()\n`)

const output = ref('')
const isRunning = ref(false)
const aiEvaluation = ref<{ type: 'success' | 'warning' | 'error' | 'info', message: string } | null>(null)

// 当前选中的知识点（用于 teach/practice 模式获取后端数据）
const activeNode = computed(() => {
  if (!appStore.panelNodeId) return null
  return knowledgeStore.getNodeById(appStore.panelNodeId)
})

// Teach 模式内容 — 来自后端知识点 aiSummary
const teachContent = computed(() => {
  const node = activeNode.value
  if (!node?.aiSummary) {
    return {
      title: node?.name || 'Python 知识点',
      overview: node?.description || '请先选择一个知识点',
      keyPoints: [] as string[],
      commonPitfalls: [] as string[],
      codeSnippet: ''
    }
  }
  return {
    title: node.name,
    overview: node.aiSummary.overview || node.description,
    keyPoints: node.aiSummary.keyPoints || [],
    commonPitfalls: node.aiSummary.commonPitfalls || [],
    codeSnippet: node.aiSummary.recommendedCodeSnippet || ''
  }
})

// Practice 模式数据 — 从后端加载
const currentPractice = computed(() => practiceStore.currentPractice)
const practiceLoading = computed(() => practiceStore.loading)

watch(() => appStore.workspaceMode, async (newMode) => {
  output.value = ''
  aiEvaluation.value = null
  isRunning.value = false

  if (newMode === 'teach') {
    // 载入知识点的教学代码
    const snippet = teachContent.value.codeSnippet
    code.value = snippet || `# ${teachContent.value.title}\n# 暂无示例代码\nprint("${teachContent.value.title}")\n`
  } else if (newMode === 'practice') {
    // 从后端加载当前知识点的练习题
    const nodeId = activeNode.value?.id
    if (nodeId) {
      await practiceStore.fetchPracticesByNode(nodeId)
      if (practiceStore.practices.length > 0) {
        practiceStore.currentPractice = practiceStore.practices[0]
        code.value = practiceStore.currentPractice.starterCode || '# 在此编写代码\n'
      } else {
        code.value = '# 暂无练习题，请先选择知识点\n'
      }
    } else {
      code.value = '# 请先选择一个知识点\n'
    }
  } else {
    code.value = `# 自由编码区\ndef hello():\n    print("Welcome to PyPad Python Learning OS!")\n\nhello()\n`
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

const editorRef = shallowRef<any>(null)
const monacoRef = shallowRef<any>(null)
let errorDecorations: string[] = []

const handleMount = (editor: any, monaco: any) => {
  editorRef.value = editor
  monacoRef.value = monaco
}

const runCode = async () => {
  isRunning.value = true
  output.value = ''
  aiEvaluation.value = null
  workspaceStore.currentCode = code.value

  // Clear previous error decorations
  if (editorRef.value && monacoRef.value) {
    errorDecorations = editorRef.value.deltaDecorations(errorDecorations, [])
  }

  try {
    const run: any = await workspaceStore.runCode()
    if (run) {
      const parts: string[] = []
      if (run.stdout) parts.push(run.stdout)
      if (run.stderr) parts.push(`[stderr] ${run.stderr}`)
      parts.push(`\n> Done in ${(run.runtimeMs / 1000).toFixed(2)}s (exit ${run.exitCode})`)
      output.value = parts.join('\n')

      if (run.exitCode === 0) {
        aiEvaluation.value = { type: 'success', message: '代码运行成功，通过全量逻辑校验！' }
      } else {
        const errorDetail = run.errorDetail
        if (errorDetail?.lineNumber && editorRef.value && monacoRef.value) {
          const lineNum = errorDetail.lineNumber
          errorDecorations = editorRef.value.deltaDecorations(errorDecorations, [
            {
              range: new monacoRef.value.Range(lineNum, 1, lineNum, 100),
              options: {
                isWholeLine: true,
                className: 'monaco-error-line-highlight',
                glyphMarginClassName: 'monaco-error-glyph'
              }
            }
          ])
          editorRef.value.revealLineInCenter(lineNum)
        }
        const adviceMsg = errorDetail?.chineseAdvice || `执行出错 (exit code ${run.exitCode})`
        aiEvaluation.value = { type: 'error', message: adviceMsg }
      }
    }
  } catch (err: any) {
    output.value = `Error: ${err.message || 'Execution failed'}`
    aiEvaluation.value = { type: 'error', message: '服务异常，无法完成代码运行' }
  } finally {
    isRunning.value = false
  }
}

// AI Review — 调用后端 /api/workspace/ai-review
const aiReview = async () => {
  isRunning.value = true
  aiEvaluation.value = null

  // 先运行代码获取 runId
  workspaceStore.currentCode = code.value
  try {
    const run: any = await workspaceStore.runCode()
    if (run?.id) {
      const review: any = await workspaceApi.requestAIReview(run.id)
      const reviewData = review?.review || review
      if (reviewData) {
        aiEvaluation.value = {
          type: reviewData.overallScore >= 80 ? 'success' : reviewData.overallScore >= 60 ? 'warning' : 'error',
          message: `代码评分: ${reviewData.overallScore}/100\n${reviewData.aiFeedback || ''}\n${(reviewData.suggestions || []).map((s: string) => `• ${s}`).join('\n')}`
        }
      }
    }
  } catch (err: any) {
    aiEvaluation.value = { type: 'error', message: 'AI 代码审查失败，请检查后端服务。' }
  } finally {
    isRunning.value = false
  }
}

// AI Explain — 调用后端 /api/agent/chat
const explainCode = async () => {
  isRunning.value = true
  aiEvaluation.value = null
  try {
    const res: any = await agentApi.chat({
      message: `请解释以下 Python 代码的功能和逻辑：\n\`\`\`python\n${code.value}\n\`\`\``,
      agentType: 'coder',
      knowledgeId: activeNode.value?.id,
    })
    aiEvaluation.value = {
      type: 'info',
      message: res?.message || '无法获取代码解释'
    }
  } catch (err) {
    aiEvaluation.value = { type: 'error', message: 'AI 代码解释失败，请检查后端服务。' }
  } finally {
    isRunning.value = false
  }
}

// Submit Practice — 调用后端 /api/practices/{id}/submit
const submitCode = async () => {
  const practice = currentPractice.value
  if (!practice) {
    aiEvaluation.value = { type: 'warning', message: '请先选择一个练习题。' }
    return
  }

  isRunning.value = true
  output.value = ''
  aiEvaluation.value = null

  try {
    const res: any = await practiceApi.submitPractice(practice.id, code.value)
    const parts: string[] = []
    parts.push(`> 练习提交结果: ${res.passed ? '✅ 通过' : '❌ 未通过'}`)
    parts.push(`> 得分: ${res.score}/100`)
    if (res.details?.length) {
      parts.push('\n测试用例详情:')
      res.details.forEach((d: any, i: number) => {
        parts.push(`  Test ${i + 1}: ${d.passed ? '✅' : '❌'} 期望: ${d.expected}  实际: ${d.actual}`)
      })
    }
    parts.push(`\n${res.feedback || ''}`)
    output.value = parts.join('\n')

    aiEvaluation.value = {
      type: res.passed ? 'success' : 'error',
      message: res.feedback || (res.passed ? '全部测试通过！' : '部分测试未通过，请检查代码。')
    }
  } catch (err: any) {
    output.value = `Error: ${err.message || '提交失败'}`
    aiEvaluation.value = { type: 'error', message: '练习提交失败，请检查后端服务。' }
  } finally {
    isRunning.value = false
  }
}

// Hint — 调用后端 /api/agent/chat 获取提示
const hintCode = async () => {
  isRunning.value = true
  aiEvaluation.value = null
  const practice = currentPractice.value
  const hintContext = practice
    ? `练习题「${practice.title}」: ${practice.prompt}\n用户当前代码:\n\`\`\`python\n${code.value}\n\`\`\`\n请给出简短提示，不要直接给出答案。`
    : `用户正在编写代码:\n\`\`\`python\n${code.value}\n\`\`\`\n请给出改进建议。`

  try {
    const res: any = await agentApi.chat({
      message: hintContext,
      agentType: 'practice',
      knowledgeId: activeNode.value?.id,
    })
    aiEvaluation.value = {
      type: 'info',
      message: res?.message || '暂无提示'
    }
  } catch (err) {
    aiEvaluation.value = { type: 'error', message: '获取提示失败，请检查后端服务。' }
  } finally {
    isRunning.value = false
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
                <h2>{{ teachContent.title }}</h2>
                <p>{{ teachContent.overview }}</p>
                
                <template v-if="teachContent.keyPoints.length > 0">
                  <h4>核心要点</h4>
                  <ul>
                    <li v-for="(point, idx) in teachContent.keyPoints" :key="idx">{{ point }}</li>
                  </ul>
                </template>

                <template v-if="teachContent.commonPitfalls.length > 0">
                  <h4>常见陷阱</h4>
                  <ul>
                    <li v-for="(pitfall, idx) in teachContent.commonPitfalls" :key="idx">{{ pitfall }}</li>
                  </ul>
                </template>
              </div>
            </div>

            <!-- PRACTICE MODE -->
            <div v-else-if="appStore.workspaceMode === 'practice'" class="panel-inner practice-panel">
              <div class="panel-header-small">
                <h3>实战练习</h3>
                <span class="badge warning-badge">Challenge</span>
              </div>
              <div v-if="practiceLoading" class="practice-content">
                <p>加载练习题中...</p>
              </div>
              <div v-else-if="currentPractice" class="practice-content">
                <h2>{{ currentPractice.title }}</h2>
                <p>{{ currentPractice.prompt }}</p>
                
                <div v-if="currentPractice.testCases?.length > 0" class="test-cases">
                  <h4>测试用例</h4>
                  <div v-for="(tc, idx) in currentPractice.testCases" :key="idx" class="test-case">
                    <span class="test-label">输入: <code>{{ tc.input || '无' }}</code></span>
                    <span class="test-expected">预期输出: <code>{{ tc.expectedOutput }}</code></span>
                  </div>
                </div>
              </div>
              <div v-else class="practice-content">
                <p>暂无练习题，请先选择一个知识点。</p>
              </div>
            </div>

            <!-- CODE MODE (AI Tutor) -->
            <div v-else class="panel-inner ai-tutor-panel">
              <div class="panel-header-small">
                <h3>AI Tutor</h3>
                <span class="badge">Active</span>
              </div>
              
              <div class="tutor-section">
                <h4>当前知识点</h4>
                <p class="tutor-text">{{ activeNode?.name || '自由编码模式' }}</p>
              </div>
              
              <div v-if="activeNode" class="tutor-section">
                <h4>知识描述</h4>
                <p class="tutor-text">{{ activeNode.description }}</p>
              </div>
              
              <div class="tutor-section task-section">
                <h4>快速操作</h4>
                <div class="task-card" @click="explainCode" style="cursor: pointer">
                  <div class="task-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                  <div class="task-details">
                    <h5>AI 代码解释</h5>
                    <p>点击获取当前代码的详细解释</p>
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

:deep(.monaco-error-line-highlight) {
  background-color: rgba(255, 59, 48, 0.15) !important;
  border-left: 4px solid #ff3b30 !important;
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
