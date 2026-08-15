import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 — auto-attach JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 认证API
export const authApi = {
  register: (data: { username: string; email: string; password: string; displayName?: string }) =>
    apiClient.post('/api/auth/register', data),
  login: (data: { username: string; password: string }) =>
    apiClient.post('/api/auth/login', data),
  me: () => apiClient.get('/api/auth/me'),
}

// 知识相关API
export const knowledgeApi = {
  getNodes: () => apiClient.get('/api/knowledge/nodes'),
  getNode: (id: string) => apiClient.get(`/api/knowledge/nodes/${id}`),
  getRelations: () => apiClient.get('/api/knowledge/relations'),
  getCategories: () => apiClient.get('/api/knowledge/categories')
}

// 用户学习API
export const userApi = {
  getKnowledge: (userId?: string) =>
    apiClient.get('/api/user/knowledge', { params: userId ? { user_id: userId } : {} }),
  updateKnowledge: (data: { userId: string; knowledgeId: string; masteryScore: number }) =>
    apiClient.post('/api/user/knowledge', data),
  recordStudy: (data: { userId: string; knowledgeId: string; duration: number; behavior: string }) =>
    apiClient.post('/api/user/study', data),
  getStudyRecords: (userId?: string, limit: number = 10) =>
    apiClient.get('/api/user/study-records', { params: { ...(userId ? { user_id: userId } : {}), limit } })
}

// Agent API
export const agentApi = {
  chat: (data: { message: string; agentType?: string; knowledgeId?: string }) =>
    apiClient.post('/api/agent/chat', data),
  getHistory: (agentType: string = 'tutor', limit: number = 50) =>
    apiClient.get('/api/agent/history', { params: { agentType, limit } }),
  generatePlan: (goal: string) =>
    apiClient.post('/api/agent/plan', null, { params: { goal } }),
  generatePractice: (knowledgeId: string, difficulty: string = 'medium') =>
    apiClient.post('/api/agent/practice', null, { params: { knowledgeId, difficulty } })
}

// Dashboard API
export const dashboardApi = {
  getOverview: (userId?: string) =>
    apiClient.get('/api/dashboard/overview', { params: userId ? { userId } : {} }),
  getProgress: (userId?: string) =>
    apiClient.get('/api/dashboard/progress', { params: userId ? { userId } : {} }),
}

// 课程API
export const courseApi = {
  getCourses: () => apiClient.get('/api/courses'),
  getCourse: (id: string) => apiClient.get(`/api/courses/${id}`),
  getCourseTree: (id: string) => apiClient.get(`/api/courses/${id}/tree`),
}

// 章节API
export const chapterApi = {
  getChapters: (courseId?: string) =>
    apiClient.get('/api/chapters', { params: courseId ? { courseId } : {} }),
  getSections: (chapterId: string) =>
    apiClient.get(`/api/chapters/${chapterId}/sections`),
}

// 项目API
export const projectApi = {
  getProjects: () => apiClient.get('/api/projects'),
  getProject: (id: string) => apiClient.get(`/api/projects/${id}`),
}

// 练习API
export const practiceApi = {
  getPracticesByNode: (knowledgeId: string) =>
    apiClient.get('/api/practices', { params: { knowledgeId } }),
  generateAIPractice: (knowledgeId: string, difficulty: string = 'medium') =>
    apiClient.post('/api/practices/generate-ai', { knowledgeId, difficulty }),
  submitPractice: (practiceId: string, code: string) =>
    apiClient.post(`/api/practices/${practiceId}/submit`, { code }),
}

// 学习会话API
export const sessionApi = {
  startSession: (data: { userId: string; knowledgeNodeId: string; courseId?: string; chapterId?: string; sectionId?: string }) =>
    apiClient.post('/api/sessions/start', data),
  recordEvent: (sessionId: string, eventType: string, payload: Record<string, any> = {}) =>
    apiClient.post(`/api/sessions/${sessionId}/events`, { eventType, payload }),
  endSession: (sessionId: string) =>
    apiClient.post(`/api/sessions/${sessionId}/end`),
  getTimeline: (sessionId: string) =>
    apiClient.get(`/api/sessions/${sessionId}/timeline`),
}

// 工作区API
export const workspaceApi = {
  runCode: (data: { sessionId: string; code: string; language?: string; practiceId?: string }) =>
    apiClient.post('/api/workspace/run', data),
  getRunHistory: (sessionId: string) =>
    apiClient.get(`/api/workspace/runs/${sessionId}`),
  requestAIReview: (runId: string) =>
    apiClient.post('/api/workspace/ai-review', { runId }),
  requestStyleReview: (runId: string) =>
    apiClient.post('/api/workspace/style-review', { runId }),
}

// 代码审查API
export const reviewApi = {
  getReview: (id: string) => apiClient.get(`/api/reviews/${id}`),
  getUserReviews: (userId: string) => apiClient.get(`/api/reviews/user/${userId}`),
}

// 分析API
export const analyticsApi = {
  getOverview: (userId?: string) =>
    apiClient.get('/api/analytics/overview', { params: userId ? { user_id: userId } : {} })
}

// 教材API
export const textbookApi = {
  upload: (data: { content: string; bookTitle?: string }) =>
    apiClient.post('/api/textbook/upload', data),
}

// 学习路径推荐API
export const recommendApi = {
  getPath: (userId?: string) =>
    apiClient.get('/api/user/recommend-path', { params: userId ? { user_id: userId } : {} }),
}

export default apiClient