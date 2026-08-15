import { MASTERY_COLORS, MASTERY_THRESHOLDS } from './constants'

export function getMasteryColor(score: number): string {
  if (score >= MASTERY_THRESHOLDS.excellent) return MASTERY_COLORS.excellent
  if (score >= MASTERY_THRESHOLDS.good) return MASTERY_COLORS.good
  return MASTERY_COLORS.weak
}

export function getMasteryLabel(score: number): string {
  if (score >= MASTERY_THRESHOLDS.excellent) return '精通'
  if (score >= MASTERY_THRESHOLDS.good) return '掌握中'
  return '薄弱'
}

export function getMasteryOpacity(score: number): number {
  return 0.3 + (score / 100) * 0.7
}
