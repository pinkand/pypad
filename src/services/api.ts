import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
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

// 知识相关API
export const knowledgeApi = {
  getNodes: () => apiClient.get('/api/knowledge/nodes'),
  getNode: (id: string) => apiClient.get(`/api/knowledge/nodes/${id}`),
  getRelations: () => apiClient.get('/api/knowledge/relations'),
  getCategories: () => apiClient.get('/api/knowledge/categories')
}

// 用户学习API
export const userApi = {
  getKnowledge: (userId: string = 'user-1') => 
    apiClient.get('/api/user/knowledge', { params: { user_id: userId } }),
  updateKnowledge: (data: { userId: string; knowledgeId: string; masteryScore: number }) =>
    apiClient.post('/api/user/knowledge', data),
  recordStudy: (data: { userId: string; knowledgeId: string; duration: number; behavior: string }) =>
    apiClient.post('/api/user/study', data),
  getStudyRecords: (userId: string = 'user-1', limit: number = 10) =>
    apiClient.get('/api/user/study-records', { params: { user_id: userId, limit } })
}

// Agent API
export const agentApi = {
  chat: (data: { message: string; agentType?: string; knowledgeId?: string }) =>
    apiClient.post('/api/agent/chat', data),
  generatePlan: (goal: string) =>
    apiClient.post('/api/agent/plan', null, { params: { goal } }),
  generatePractice: (knowledgeId: string, difficulty: string = 'medium') =>
    apiClient.post('/api/agent/practice', null, { params: { knowledgeId, difficulty } })
}

// 分析API
export const analyticsApi = {
  getOverview: (userId: string = 'user-1') =>
    apiClient.get('/api/analytics/overview', { params: { user_id: userId } })
}

export default apiClient