<template>
  <nav class="nav">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">
        <span class="logo-dot"></span>
        系统首页
      </router-link>
      <div class="nav-links">
        <router-link to="/" class="nav-link" exact-active-class="active">首页</router-link>
        <router-link to="/crawler" class="nav-link" exact-active-class="active">爬虫管理</router-link>
        <router-link to="/profile" class="nav-link" exact-active-class="active">个人中心</router-link>
        <div class="nav-user">
          <div class="user-avatar">{{ authStore.user?.username?.charAt(0)?.toUpperCase() }}</div>
          <span class="user-name">{{ authStore.user?.username }}</span>
          <button class="btn-logout" @click="handleLogout">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            退出
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05), 0 4px 24px rgba(0, 0, 0, 0.06);
  padding: 0 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.nav-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--gray-800);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: -0.3px;
}

.logo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
  display: inline-block;
}

.nav-links {
  display: flex;
  gap: 4px;
  align-items: center;
}

.nav-link {
  color: var(--gray-500);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: -0.1px;
}

.nav-link:hover {
  color: var(--gray-800);
  background: rgba(0, 0, 0, 0.04);
}

.nav-link.active {
  color: var(--primary-700);
  background: rgba(76, 110, 245, 0.08);
  font-weight: 600;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 12px;
  padding-left: 16px;
  border-left: 1px solid rgba(0, 0, 0, 0.06);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(76, 110, 245, 0.25);
}

.user-name {
  font-size: 14px;
  color: var(--gray-700);
  font-weight: 600;
  letter-spacing: -0.1px;
}

.btn-logout {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  color: #ef4444;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-logout:hover {
  background: #ef4444;
  color: #fff;
  box-shadow: 0 2px 12px rgba(239, 68, 68, 0.3);
}

.btn-logout:active {
  transform: scale(0.96);
}

.logout-icon {
  width: 15px;
  height: 15px;
}
</style>