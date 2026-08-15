export interface UserProfile {
  id: string
  name: string
  email: string
  avatar?: string
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
