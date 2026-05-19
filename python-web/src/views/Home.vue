<template>
  <div>
    <NavBar />
    
    <div class="home-container">
      <div class="welcome-card">
        <h1 class="welcome-title">欢迎回来，{{ authStore.user?.username }}！</h1>
        <p class="welcome-text">登录系统成功，这是首页内容。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>
