export type AgentType = 'planner' | 'tutor' | 'coder' | 'practice' | 'memory'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  agentType: AgentType
  timestamp: string
  metadata?: Record<string, unknown>
}

export interface Task {
  id: string
  title: string
  description: string
  knowledgeId: string
  type: 'learn' | 'practice' | 'debug' | 'review'
  status: 'pending' | 'in_progress' | 'completed'
  difficulty: 'easy' | 'medium' | 'hard'
  content?: string
  solution?: string
  createdAt: string
}

export interface Recommendation {
  id: string
  knowledgeId: string
  reason: string
  priority: number
  type: 'review' | 'learn' | 'practice'
}

export interface AgentMemory {
  userId: string
  agentType: AgentType
  memory: Record<string, unknown>
  updatedAt: string
}
