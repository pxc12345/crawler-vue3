<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBlessingStore } from '@/stores/blessing'
import { login } from '@/utils/api'

const router = useRouter()
const store = useBlessingStore()

const username = ref('')
const loading = ref(false)

onMounted(() => {
  window.__showToast = showToast
})

function showToast(msg: string) {
  const el = document.createElement('div')
  el.className = 'toast'
  el.textContent = msg
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 2000)
}

async function handleLogin() {
  const name = username.value.trim()
  if (!name) {
    showToast('请输入专属账号')
    return
  }
  loading.value = true
  try {
    const res: any = await login(name)
    if (res.code === 200) {
      const data = res.data
      if (data.role === 'admin') {
        store.setUser('admin', 'admin', '#fef5f8', '#333333')
        router.push('/admin')
      } else {
        store.setUser(data.username, 'user', data.bg_color, data.text_color, data.theme, data.effect_profile)
        router.push('/show')
      }
    } else {
      showToast(res.msg || '账号无效，请重新输入')
    }
  } catch {
    showToast('网络请求失败，请检查连接')
  } finally {
    loading.value = false
  }
}

declare global {
  interface Window {
    __showToast: (msg: string) => void
  }
}
window.__showToast = showToast
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-icon">🎀</div>
      <h1 class="login-title">专属祝福入口</h1>
      <p class="login-subtitle">输入你的专属账号，开启温馨祝福</p>
      <div class="login-form">
        <input
          v-model="username"
          class="input-field login-input"
          type="text"
          placeholder="请输入专属账号"
          maxlength="30"
          @keyup.enter="handleLogin"
        />
        <button
          class="btn-primary login-btn"
          :disabled="!username.trim() || loading"
          @click="handleLogin"
        >
          {{ loading ? '进入中...' : '立即进入' }}
        </button>
      </div>
      <p class="login-footer">专属定制祝福，只为一人</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #fef5f8 0%, #fce4ec 50%, #f8bbd0 100%);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 360px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 40px 28px 32px;
  box-shadow: 0 16px 48px rgba(255, 105, 135, 0.12);
  animation: scaleIn 0.5s ease-out;
  text-align: center;
}

.login-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.login-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #d4687c;
  margin-bottom: 8px;
  letter-spacing: 0.03em;
}

.login-subtitle {
  font-size: 0.88rem;
  color: #b0a0a8;
  margin-bottom: 28px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-input {
  text-align: center;
}

.login-btn {
  width: 100%;
}

.login-footer {
  margin-top: 28px;
  font-size: 0.75rem;
  color: #c8b8c0;
  letter-spacing: 0.04em;
}
</style>
