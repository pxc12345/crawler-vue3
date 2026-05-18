<template>
  <div class="container">
    <div class="card">
      <h1 class="card-title">注册</h1>
      
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>
      
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="username"
            type="text"
            class="form-input"
            :class="{ error: usernameError }"
            placeholder="请输入用户名（至少3位）"
          />
          <div v-if="usernameError" class="error-message">{{ usernameError }}</div>
        </div>
        
        <div class="form-group">
          <label class="form-label">邮箱（可选）</label>
          <input
            v-model="email"
            type="email"
            class="form-input"
            :class="{ error: emailError }"
            placeholder="请输入邮箱"
          />
          <div v-if="emailError" class="error-message">{{ emailError }}</div>
        </div>
        
        <div class="form-group">
          <label class="form-label">手机号（可选）</label>
          <input
            v-model="phone"
            type="tel"
            class="form-input"
            :class="{ error: phoneError }"
            placeholder="请输入手机号"
          />
          <div v-if="phoneError" class="error-message">{{ phoneError }}</div>
        </div>
        
        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="password-input-wrapper">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ error: passwordError }"
              placeholder="请输入密码（至少6位）"
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
          <label class="form-label">确认密码</label>
          <div class="password-input-wrapper">
            <input
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ error: confirmPasswordError }"
              placeholder="请再次输入密码"
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
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="text-center mt-30">
        已有账号？
        <router-link to="/login" class="link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const usernameError = ref('')
const emailError = ref('')
const phoneError = ref('')
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
  usernameError.value = ''
  emailError.value = ''
  phoneError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!username.value.trim()) {
    usernameError.value = '请输入用户名'
    return false
  }
  if (username.value.length < 3) {
    usernameError.value = '用户名至少3位'
    return false
  }
  
  if (email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    emailError.value = '请输入有效的邮箱'
    return false
  }
  
  if (phone.value && !/^1[3-9]\d{9}$/.test(phone.value)) {
    phoneError.value = '请输入有效的手机号'
    return false
  }
  
  if (!password.value) {
    passwordError.value = '请输入密码'
    return false
  }
  if (password.value.length < 6) {
    passwordError.value = '密码至少6位'
    return false
  }
  
  if (!confirmPassword.value) {
    confirmPasswordError.value = '请确认密码'
    return false
  }
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次密码不一致'
    return false
  }
  
  return true
}

async function handleRegister() {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    const result = await authStore.register(
      username.value,
      password.value,
      email.value || null,
      phone.value || null
    )
    
    if (result.success) {
      successMessage.value = '注册成功！即将跳转到登录页...'
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      errorMessage.value = result.message || '注册失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
