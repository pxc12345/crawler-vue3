<template>
  <div class="container">
    <div class="card">
      <h1 class="card-title">重置密码</h1>
      
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>
      
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>
      
      <template v-if="!resetSuccess">
        <form @submit.prevent="handleReset">
          <div class="form-group">
            <label class="form-label">新密码</label>
            <div class="password-input-wrapper">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                :class="{ error: passwordError }"
                placeholder="请输入新密码（至少6位）"
                @input="checkPasswordStrength"
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
            
            <div class="password-strength">
              <div class="strength-bar">
                <div
                  class="strength-fill"
                  :style="{
                    width: strengthPercent,
                    backgroundColor: strengthColor
                  }"
                ></div>
              </div>
              <div class="strength-text" :style="{ color: strengthColor }">
                {{ strengthText }}
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <div class="password-input-wrapper">
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                class="form-input"
                :class="{ error: confirmPasswordError }"
                placeholder="请再次输入新密码"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                {{ showConfirmPassword ? '隐藏' : '显示' }}
              </button>
            </div>
            <div v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
          </div>
          
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '重置中...' : '重置密码' }}
          </button>
        </form>
      </template>
      
      <template v-else>
        <div class="success-page">
          <div class="success-icon">✅</div>
          <h2 class="success-title">密码重置成功！</h2>
          <p class="success-text">请使用新密码登录</p>
          <button class="btn btn-primary" @click="goToLogin">
            去登录
          </button>
        </div>
      </template>
      
      <div v-if="!resetSuccess" class="text-center mt-30">
        <router-link to="/login" class="link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authAPI } from '../api'

const router = useRouter()
const route = useRoute()

const userId = ref(null)
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const resetSuccess = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

const strengthPercent = computed(() => {
  if (!password.value) return '0%'
  const strength = calculateStrength(password.value)
  return `${strength * 25}%`
})

const strengthColor = computed(() => {
  if (!password.value) return 'var(--gray-300)'
  const strength = calculateStrength(password.value)
  const colors = ['var(--error)', 'var(--warning)', 'var(--primary-400)', 'var(--success)']
  return colors[Math.min(strength - 1, 3)]
})

const strengthText = computed(() => {
  if (!password.value) return '请输入密码'
  const strength = calculateStrength(password.value)
  const texts = ['弱', '一般', '较强', '强']
  return texts[Math.min(strength - 1, 3)]
})

function calculateStrength(pwd) {
  let score = 0
  if (pwd.length >= 6) score++
  if (pwd.length >= 10) score++
  if (/[A-Z]/.test(pwd)) score++
  if (/[0-9]/.test(pwd)) score++
  if (/[^A-Za-z0-9]/.test(pwd)) score++
  return Math.max(1, Math.min(4, score))
}

function checkPasswordStrength() {
  calculateStrength(password.value)
}

function validateForm() {
  passwordError.value = ''
  confirmPasswordError.value = ''
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!password.value) {
    passwordError.value = '请输入新密码'
    return false
  }
  if (password.value.length < 6) {
    passwordError.value = '密码至少6位'
    return false
  }
  
  if (!confirmPassword.value) {
    confirmPasswordError.value = '请确认新密码'
    return false
  }
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次密码不一致'
    return false
  }
  
  return true
}

async function handleReset() {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    const response = await authAPI.resetPassword({
      user_id: userId.value,
      new_password: password.value
    })
    
    if (response.data.success) {
      resetSuccess.value = true
    } else {
      errorMessage.value = response.data.message || '重置失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.push('/login')
}

onMounted(() => {
  userId.value = route.query.user_id
  if (!userId.value) {
    router.push('/forgot-password')
  }
})
</script>
