<template>
  <div class="container">
    <div class="card">
      <h1 class="card-title">忘记密码</h1>
      
      <div v-if="errorMessage" class="alert alert-error">
        {{ errorMessage }}
      </div>
      
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>
      
      <template v-if="step === 1">
        <form @submit.prevent="sendCode">
          <div class="form-group">
            <label class="form-label">请输入注册邮箱或手机号</label>
            <div class="code-input-group">
              <input
                v-model="target"
                type="text"
                class="form-input code-input"
                :class="{ error: targetError }"
                placeholder="邮箱或手机号"
              />
            </div>
            <div v-if="targetError" class="error-message">{{ targetError }}</div>
          </div>
          
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '发送中...' : '发送验证码' }}
          </button>
        </form>
      </template>
      
      <template v-else-if="step === 2">
        <form @submit.prevent="verifyCode">
          <div class="form-group">
            <label class="form-label">验证码已发送至 {{ target }}</label>
            <div class="code-input-group">
              <input
                v-model="code"
                type="text"
                class="form-input code-input"
                :class="{ error: codeError }"
                placeholder="请输入验证码"
                maxlength="6"
              />
              <button
                type="button"
                class="btn btn-secondary btn-send-code"
                :disabled="countdown > 0"
                @click="resendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : '重新发送' }}
              </button>
            </div>
            <div v-if="codeError" class="error-message">{{ codeError }}</div>
          </div>
          
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '验证中...' : '验证' }}
          </button>
        </form>
      </template>
      
      <div class="text-center mt-30">
        <router-link to="/login" class="link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api'

const router = useRouter()

const step = ref(1)
const target = ref('')
const code = ref('')
const userId = ref(null)
const loading = ref(false)
const countdown = ref(0)
const errorMessage = ref('')
const successMessage = ref('')
const targetError = ref('')
const codeError = ref('')

let countdownTimer = null

function validateTarget() {
  targetError.value = ''
  const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(target.value)
  const isPhone = /^1[3-9]\d{9}$/.test(target.value)
  
  if (!target.value.trim()) {
    targetError.value = '请输入邮箱或手机号'
    return false
  }
  if (!isEmail && !isPhone) {
    targetError.value = '请输入有效的邮箱或手机号'
    return false
  }
  return true
}

function startCountdown() {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

async function sendCode() {
  if (!validateTarget()) return
  
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    const response = await authAPI.sendForgotPasswordCode(target.value)
    
    if (response.data.success) {
      userId.value = response.data.data.user_id
      step.value = 2
      startCountdown()
      successMessage.value = '验证码已发送'
    } else {
      errorMessage.value = response.data.message || '发送失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function resendCode() {
  await sendCode()
}

async function verifyCode() {
  codeError.value = ''
  errorMessage.value = ''
  
  if (!code.value.trim()) {
    codeError.value = '请输入验证码'
    return
  }
  
  loading.value = true
  
  try {
    const response = await authAPI.verifyForgotPasswordCode({
      user_id: userId.value,
      code: code.value,
      target: target.value
    })
    
    if (response.data.success) {
      router.push({
        path: '/reset-password',
        query: { user_id: userId.value }
      })
    } else {
      errorMessage.value = response.data.message || '验证码错误'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
