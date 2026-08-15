<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const displayName = ref('')
const errorMsg = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  errorMsg.value = ''
  loading.value = true
  try {
    if (isLogin.value) {
      await userStore.login(username.value, password.value)
    } else {
      await userStore.register(username.value, email.value, password.value, displayName.value)
    }
    router.push('/')
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || err?.message || '操作失败'
  } finally {
    loading.value = false
  }
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMsg.value = ''
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <div class="w-full max-w-md p-8">
      <div class="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl">
        <!-- Logo -->
        <div class="text-center mb-8">
          <div class="text-4xl mb-2">🐍</div>
          <h1 class="text-2xl font-bold text-white">PyPad</h1>
          <p class="text-sm text-white/50 mt-1">{{ isLogin ? '登录你的账号' : '创建新账号' }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm text-white/60 mb-1">用户名</label>
            <input
              v-model="username"
              type="text"
              required
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-purple-500 transition"
              placeholder="输入用户名"
            />
          </div>

          <div v-if="!isLogin">
            <label class="block text-sm text-white/60 mb-1">邮箱</label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-purple-500 transition"
              placeholder="输入邮箱"
            />
          </div>

          <div v-if="!isLogin">
            <label class="block text-sm text-white/60 mb-1">显示名称</label>
            <input
              v-model="displayName"
              type="text"
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-purple-500 transition"
              placeholder="可选"
            />
          </div>

          <div>
            <label class="block text-sm text-white/60 mb-1">密码</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-purple-500 transition"
              placeholder="输入密码"
            />
          </div>

          <div v-if="errorMsg" class="text-red-400 text-sm text-center bg-red-500/10 py-2 rounded-lg">
            {{ errorMsg }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium rounded-lg transition"
          >
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>

        <!-- Toggle -->
        <div class="mt-6 text-center">
          <button @click="toggleMode" class="text-sm text-purple-400 hover:text-purple-300 transition">
            {{ isLogin ? '没有账号？立即注册' : '已有账号？去登录' }}
          </button>
        </div>

        <!-- Skip -->
        <div class="mt-4 text-center">
          <router-link to="/" class="text-xs text-white/30 hover:text-white/50 transition">
            跳过，先看看 →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
