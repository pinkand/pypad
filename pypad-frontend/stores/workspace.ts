import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { WorkspaceRun, CodeReview, VariablesMap, StyleReview } from '@/types/knowledge'
import { workspaceApi } from '@/services/api'
import { useSessionStore } from './session'

export const useWorkspaceStore = defineStore('workspace', () => {
  const currentCode = ref<string>('# PyPad\nprint("Hello PyPad")\n')
  const stdout = ref<string>('')
  const stderr = ref<string>('')
  const exitCode = ref<number>(0)
  const runtimeMs = ref<number>(0)
  const memoryBytes = ref<number>(0)
  const isExecuting = ref<boolean>(false)
  const variables = ref<VariablesMap | null>(null)
  const styleReview = ref<StyleReview | null>(null)

  const runHistory = ref<WorkspaceRun[]>([])
  const latestReview = ref<CodeReview | null>(null)

  const sessionStore = useSessionStore()

  const runCode = async (practiceId?: string) => {
    isExecuting.value = true
    stdout.value = ''
    stderr.value = ''
    variables.value = null

    const sessionId = sessionStore.currentSession?.id || 'default-session'

    try {
      const res: any = await workspaceApi.runCode({
        sessionId,
        code: currentCode.value,
        language: 'python',
        practiceId
      })

      stdout.value = res.stdout || ''
      stderr.value = res.stderr || ''
      exitCode.value = res.exitCode ?? 0
      runtimeMs.value = res.runtimeMs ?? 42
      memoryBytes.value = res.memoryBytes ?? 1024 * 512
      variables.value = res.variables || null

      const runRecord: WorkspaceRun = {
        id: res.id || `run-${Date.now()}`,
        sessionId,
        practiceId,
        code: currentCode.value,
        language: 'python',
        status: res.status || (res.exitCode === 0 ? 'success' : 'runtime_error'),
        stdout: stdout.value,
        stderr: stderr.value,
        exitCode: exitCode.value,
        runtimeMs: runtimeMs.value,
        memoryBytes: memoryBytes.value,
        createdAt: new Date().toISOString()
      }

      runHistory.value.unshift(runRecord)
      await sessionStore.recordEvent('run_code', { runId: runRecord.id, exitCode: runRecord.exitCode })
      return runRecord
    } catch (err: any) {
      stderr.value = err.message || 'Execution error'
      stdout.value = ''
      exitCode.value = 1
    } finally {
      isExecuting.value = false
    }
  }

  const requestAIReview = async (runId: string) => {
    try {
      const res: any = await workspaceApi.requestAIReview(runId)
      latestReview.value = res.review || res
      await sessionStore.recordEvent('ai_rated', { reviewId: latestReview.value?.id })
      return latestReview.value
    } catch (err) {
      console.error('AI Review Error:', err)
    }
  }

  const requestStyleReview = async (runId: string) => {
    try {
      const res: any = await workspaceApi.requestStyleReview(runId)
      styleReview.value = res.styleReview || res
      return styleReview.value
    } catch (err) {
      console.error('Style Review Error:', err)
      return null
    }
  }

  return {
    currentCode,
    stdout,
    stderr,
    exitCode,
    runtimeMs,
    memoryBytes,
    isExecuting,
    variables,
    styleReview,
    runHistory,
    latestReview,
    runCode,
    requestAIReview,
    requestStyleReview
  }
})
