<template>
  <div class="container">
    <div class="card">
      <div class="logo-wrapper">
        <img src="/logo.png" alt="CrawlMaster" class="login-logo" />
      </div>
      <h1 class="card-title">登录</h1>
      
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">账号（用户名/邮箱）</label>
          <input
            v-model="identifier"
            type="text"
            class="form-input"
            :class="{ error: identifierError }"
            placeholder="请输入用户名或邮箱"
          />
          <div v-if="identifierError" class="error-message">{{ identifierError }}</div>
        </div>
        
        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="password-input-wrapper">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ error: passwordError }"
              placeholder="请输入密码"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '隐藏' : '显示' }}
            </button>
          </div>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
        </div>
        
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="text-center mt-30">
        <router-link to="/forgot-password" class="link">忘记密码？</router-link>
      </div>
      
      <div class="text-center mt-20">
        还没有账号？
        <router-link to="/register" class="link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const identifier = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const identifierError = ref('')
const passwordError = ref('')

function validateForm() {
  identifierError.value = ''
  passwordError.value = ''
  errorMessage.value = ''
  
  if (!identifier.value.trim()) {
    identifierError.value = '请输入账号'
    return false
  }
  
  if (!password.value) {
    passwordError.value = '请输入密码'
    return false
  }
  
  return true
}

async function handleLogin() {
  if (!validateForm()) return
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const result = await authStore.login(identifier.value, password.value)
    
    if (result.success) {
      router.push('/')
    } else {
      errorMessage.value = result.message || '登录失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
