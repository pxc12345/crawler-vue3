<template>
  <div>
    <NavBar />
    
    <div class="home-container">
      <div class="profile-card">
        <h2 class="profile-title">个人信息</h2>
        
        <div class="profile-item">
          <span class="profile-label">用户ID</span>
          <span class="profile-value">{{ profile?.id }}</span>
        </div>
        
        <div class="profile-item">
          <span class="profile-label">用户名</span>
          <span class="profile-value">{{ profile?.username }}</span>
        </div>
        
        <div class="profile-item">
          <span class="profile-label">邮箱</span>
          <span class="profile-value">{{ profile?.email || '未绑定' }}</span>
        </div>
        
        <div class="profile-item">
          <span class="profile-label">手机号</span>
          <span class="profile-value">{{ profile?.phone || '未绑定' }}</span>
        </div>
        
        <div class="profile-item">
          <span class="profile-label">注册时间</span>
          <span class="profile-value">{{ formatDate(profile?.created_at) }}</span>
        </div>
        
        <div class="profile-item">
          <span class="profile-label">最后登录</span>
          <span class="profile-value">{{ formatDate(profile?.last_login_at) }}</span>
        </div>
      </div>
      
      <div class="profile-card mt-30">
        <h2 class="profile-title">修改密码</h2>
        
        <div v-if="errorMessage" class="alert alert-error">
          {{ errorMessage }}
        </div>
        
        <div v-if="successMessage" class="alert alert-success">
          {{ successMessage }}
        </div>
        
        <form @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <div class="password-input-wrapper">
              <input
                v-model="oldPassword"
                :type="showOldPassword ? 'text' : 'password'"
                class="form-input"
                :class="{ error: oldPasswordError }"
                placeholder="请输入当前密码"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showOldPassword = !showOldPassword"
              >
                {{ showOldPassword ? '隐藏' : '显示' }}
              </button>
            </div>
            <div v-if="oldPasswordError" class="error-message">{{ oldPasswordError }}</div>
          </div>
          
          <div class="form-group">
            <label class="form-label">新密码</label>
            <div class="password-input-wrapper">
              <input
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                class="form-input"
                :class="{ error: newPasswordError }"
                placeholder="请输入新密码（至少6位）"
                @input="checkPasswordStrength"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showNewPassword = !showNewPassword"
              >
                {{ showNewPassword ? '隐藏' : '显示' }}
              </button>
            </div>
            <div v-if="newPasswordError" class="error-message">{{ newPasswordError }}</div>
            
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
            {{ loading ? '修改中...' : '修改密码' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authAPI, userAPI } from '../api'
import NavBar from '../components/NavBar.vue'

const authStore = useAuthStore()

const profile = ref(null)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const oldPasswordError = ref('')
const newPasswordError = ref('')
const confirmPasswordError = ref('')

const strengthPercent = computed(() => {
  if (!newPassword.value) return '0%'
  const strength = calculateStrength(newPassword.value)
  return `${strength * 25}%`
})

const strengthColor = computed(() => {
  if (!newPassword.value) return 'var(--gray-300)'
  const strength = calculateStrength(newPassword.value)
  const colors = ['var(--error)', 'var(--warning)', 'var(--primary-400)', 'var(--success)']
  return colors[Math.min(strength - 1, 3)]
})

const strengthText = computed(() => {
  if (!newPassword.value) return '请输入密码'
  const strength = calculateStrength(newPassword.value)
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
  calculateStrength(newPassword.value)
}

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function validateForm() {
  oldPasswordError.value = ''
  newPasswordError.value = ''
  confirmPasswordError.value = ''
  errorMessage.value = ''
  successMessage.value = ''
  
  if (!oldPassword.value) {
    oldPasswordError.value = '请输入当前密码'
    return false
  }
  
  if (!newPassword.value) {
    newPasswordError.value = '请输入新密码'
    return false
  }
  if (newPassword.value.length < 6) {
    newPasswordError.value = '密码至少6位'
    return false
  }
  
  if (!confirmPassword.value) {
    confirmPasswordError.value = '请确认新密码'
    return false
  }
  if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次密码不一致'
    return false
  }
  
  return true
}

async function handleChangePassword() {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    const response = await authAPI.changePassword({
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    
    if (response.data.success) {
      successMessage.value = '密码修改成功'
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      errorMessage.value = response.data.message || '修改失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function loadProfile() {
  try {
    const response = await userAPI.getProfile()
    if (response.data.success) {
      profile.value = response.data.data
    }
  } catch (error) {
    console.error('加载用户信息失败', error)
  }
}

onMounted(() => {
  loadProfile()
})
</script>
