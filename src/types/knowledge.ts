export interface KnowledgeNode {
  id: string
  name: string
  description: string
  category: string
  importance: number
  icon?: string
  prerequisites: string[]
  mastery?: number
  lastStudyTime?: string
  position?: { x: number; y: number; z: number }
  
  // Tree structure fields
  parentId?: string | null
  depth?: number
  sortOrder?: number
  children?: KnowledgeNode[]
}

export interface KnowledgeEdge {
  id: string
  source: string
  target: string
  relationType: 'prerequisite' | 'related' | 'extends'
  strength: 'hard' | 'soft'
}

export interface KnowledgeCluster {
  id: string
  name: string
  category: string
  nodeIds: string[]
}

export interface LearningPath {
  id: string
  goal: string
  nodes: string[]
  progress: number
  createdAt: string
}

export interface StudyRecord {
  id: string
  knowledgeId: string
  duration: number
  behavior: 'learn' | 'practice' | 'review' | 'debug'
  result: Record<string, unknown>
  createdAt: string
}

export interface WrongQuestion {
  id: string
  knowledgeId: string
  question: string
  userAnswer: string
  correctAnswer: string
  errorReason: string
  resolved: boolean
  createdAt: string
}

export interface GraphResponse {
  tree: KnowledgeNode[]
  edges: KnowledgeEdge[]
}

export interface UserProfile {
  id: string
  name: string
  email: string
  currentGoal: string
  level: number
  experience: number
  streak: number
  createdAt: string
}

export interface UserStats {
  totalNodes: number
  masteredNodes: number
  learningNodes: number
  weakNodes: number
  totalTimeSpent: number
  averageMastery: number
}
