import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { CodeReview } from '@/types/knowledge'
import { reviewApi } from '@/services/api'
import { useUserStore } from './user'

export const useReviewStore = defineStore('review', () => {
  const reviews = ref<CodeReview[]>([])
  const currentReview = ref<CodeReview | null>(null)
  const loading = ref(false)

  const fetchUserReviews = async (userId?: string) => {
    if (!userId) {
      const userStore = useUserStore()
      userId = userStore.authUser?.id || 'user-1'
    }
    loading.value = true
    try {
      const res: any = await reviewApi.getUserReviews(userId)
      reviews.value = res.reviews || res || []
    } catch (err) {
      reviews.value = []
    } finally {
      loading.value = false
    }
  }

  const getReviewById = async (id: string) => {
    loading.value = true
    try {
      const res: any = await reviewApi.getReview(id)
      currentReview.value = res.review || res
      return currentReview.value
    } finally {
      loading.value = false
    }
  }

  return {
    reviews,
    currentReview,
    loading,
    fetchUserReviews,
    getReviewById
  }
})
