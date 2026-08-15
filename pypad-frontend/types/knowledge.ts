export interface Course {
  id: string
  title: string
  description: string
  coverUrl?: string
  level: 'beginner' | 'intermediate' | 'advanced'
  category: string
  sortOrder: number
  chapters?: Chapter[]
  createdAt: string
  updatedAt: string
}

export interface Chapter {
  id: string
  courseId: string
  title: string
  description: string
  sortOrder: number
  sections?: Section[]
}

export interface Section {
  id: string
  chapterId: string
  title: string
  contentType: 'text' | 'video' | 'interactive'
  estimatedMinutes: number
  sortOrder: number
  knowledgeNodeIds: string[]
}

export interface AISummary {
  overview: string
  keyPoints: string[]
  commonPitfalls: string[]
  recommendedCodeSnippet?: string
}

export interface NodeMastery {
  score: number
  status: 'unlearned' | 'learning' | 'mastered' | 'weak'
  lastStudiedAt?: string
}

export interface KnowledgeNode {
  id: string
  code?: string
  name: string
  description: string
  category: string
  importance: number
  icon?: string
  prerequisites: string[]
  
  // 关联体系与全图谱模型
  courseId?: string
  chapterId?: string
  sectionId?: string
  projectIds?: string[]
  practiceIds?: string[]
  aiSummary?: AISummary
  masteryScore?: number
  mastery?: NodeMastery
  lastStudyTime?: string
  
  // 视图及 3D 渲染定位字段
  position?: { x: number; y: number; z: number }
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
  weight?: number
}

export interface KnowledgeCluster {
  id: string
  name: string
  category: string
  nodeIds: string[]
}

export interface Project {
  id: string
  title: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  estimatedHours: number
  knowledgeNodeIds: string[]
  practiceIds: string[]
  initCode: string
  readmeMarkdown: string
  testCases: Array<{
    id: string
    input: string
    expectedOutput: string
    isHidden: boolean
  }>
  createdAt: string
}

export interface Practice {
  id: string
  title: string
  type: 'ai_generated' | 'fixed' | 'random' | 'exam'
  difficulty: 'easy' | 'medium' | 'hard'
  knowledgeNodeId: string
  projectId?: string
  prompt: string
  starterCode: string
  solutionCode?: string
  testCases: Array<{
    input: string
    expectedOutput: string
  }>
  aiGenParams?: Record<string, unknown>
}

export interface WorkspaceRun {
  id: string
  sessionId: string
  practiceId?: string
  code: string
  language: string
  status: 'success' | 'compile_error' | 'runtime_error' | 'timeout'
  stdout: string
  stderr: string
  exitCode: number
  runtimeMs: number
  memoryBytes: number
  aiReview?: CodeReview
  createdAt: string
}

export interface CodeReview {
  id: string
  workspaceRunId: string
  sessionId: string
  overallScore: number
  codeQualityScore: number
  logicScore: number
  performanceScore: number
  aiFeedback: string
  suggestions: string[]
  weaknessTags: string[]
  createdAt: string
}

export type SessionEventType =
  | 'open_node'
  | 'read_content'
  | 'ai_chat'
  | 'run_code'
  | 'submit_practice'
  | 'ai_rated'
  | 'close_session'

export interface SessionEventLog {
  id: string
  sessionId: string
  eventType: SessionEventType
  payload: Record<string, unknown>
  timestamp: string
}

export interface Session {
  id: string
  userId: string
  courseId?: string
  chapterId?: string
  sectionId?: string
  knowledgeNodeId: string
  status: 'active' | 'completed' | 'abandoned'
  startTime: string
  endTime?: string
  totalDurationSeconds: number
  eventLogs: SessionEventLog[]
  workspaceRuns: WorkspaceRun[]
  reviews: CodeReview[]
}

export interface UserProgress {
  userId: string
  currentCourseId?: string
  currentSessionId?: string
  overallMastery: number
  studyStreakDays: number
  completedProjectsCount: number
  completedPracticesCount: number
  totalStudyTimeSeconds: number
  weakKnowledgeNodeIds: string[]
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
  userId?: string
  knowledgeNodeId: string
  duration: number
  behavior: 'read' | 'learn' | 'practice' | 'review' | 'debug'
  result?: Record<string, unknown>
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
  nodes?: KnowledgeNode[]
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
