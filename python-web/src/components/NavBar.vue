<template>
  <nav class="nav">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">系统首页</router-link>
      <div class="nav-links">
        <router-link to="/" class="nav-link" exact-active-class="active">首页</router-link>
        <router-link to="/crawler" class="nav-link" exact-active-class="active">爬虫管理</router-link>
        <router-link to="/profile" class="nav-link" exact-active-class="active">个人中心</router-link>
        <div class="nav-user">
          <span class="user-name">{{ authStore.user?.username }}</span>
          <button class="btn-logout" @click="handleLogout">退出登录</button>
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