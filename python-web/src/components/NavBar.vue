<template>
  <nav class="nav">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">
        <img src="/logo.png" alt="CrawlMaster" class="logo-img" />
        <span class="logo-text">CrawlMaster</span>
      </router-link>

      <div class="nav-links">
        <router-link to="/" class="nav-link" exact-active-class="active">首页</router-link>

        <div class="nav-dropdown-wrapper" @mouseenter="openDropdown('tasks')" @mouseleave="closeDropdown('tasks')">
          <span class="nav-link nav-dropdown-trigger" :class="{ active: isActiveTask }">
            任务管理
            <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </span>
          <div class="nav-dropdown" :class="{ visible: activeDropdown === 'tasks' }">
            <router-link to="/tasks" class="dropdown-item">任务列表</router-link>
            <router-link to="/task-templates" class="dropdown-item">任务模板</router-link>
          </div>
        </div>

        <div class="nav-dropdown-wrapper" @mouseenter="openDropdown('data')" @mouseleave="closeDropdown('data')">
          <span class="nav-link nav-dropdown-trigger" :class="{ active: isActiveData }">
            数据管理
            <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </span>
          <div class="nav-dropdown" :class="{ visible: activeDropdown === 'data' }">
            <router-link to="/data-preview" class="dropdown-item">数据预览</router-link>
            <router-link to="/data-clean" class="dropdown-item">数据清洗</router-link>
            <router-link to="/data-export" class="dropdown-item">数据导出</router-link>
          </div>
        </div>

        <div class="nav-dropdown-wrapper" @mouseenter="openDropdown('proxy')" @mouseleave="closeDropdown('proxy')">
          <span class="nav-link nav-dropdown-trigger" :class="{ active: isActiveProxy }">
            代理管理
            <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </span>
          <div class="nav-dropdown" :class="{ visible: activeDropdown === 'proxy' }">
            <router-link to="/proxy-pool" class="dropdown-item">代理池</router-link>
            <router-link to="/anti-crawl" class="dropdown-item">风控配置</router-link>
          </div>
        </div>

        <div class="nav-dropdown-wrapper" @mouseenter="openDropdown('monitor')" @mouseleave="closeDropdown('monitor')">
          <span class="nav-link nav-dropdown-trigger" :class="{ active: isActiveMonitor }">
            系统监控
            <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </span>
          <div class="nav-dropdown" :class="{ visible: activeDropdown === 'monitor' }">
            <router-link to="/system-monitor" class="dropdown-item">资源看板</router-link>
            <router-link to="/system-logs" class="dropdown-item">系统日志</router-link>
          </div>
        </div>

        <router-link to="/alerts" class="nav-link" :class="{ active: $route.path === '/alerts' }">告警中心</router-link>

        <router-link to="/guide" class="nav-link" :class="{ active: $route.path === '/guide' }">使用说明</router-link>

        <div class="nav-user">
          <router-link to="/workspace" class="nav-user-link">工作台</router-link>
          <div class="user-avatar">{{ authStore.user?.username?.charAt(0)?.toUpperCase() }}</div>
          <span class="user-name">{{ authStore.user?.username }}</span>
          <router-link to="/settings" class="btn-settings">
            <svg class="settings-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </router-link>
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
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeDropdown = ref(null)
let closeTimer = null

const isActiveTask = computed(() => ['/tasks', '/task-templates', '/tasks/'].some(p => route.path.startsWith(p)) || /^\/tasks\/\d+/.test(route.path))
const isActiveData = computed(() => ['/data-preview', '/data-clean', '/data-export'].some(p => route.path.startsWith(p)))
const isActiveProxy = computed(() => ['/proxy-pool', '/anti-crawl'].some(p => route.path.startsWith(p)))
const isActiveMonitor = computed(() => ['/system-monitor', '/system-logs'].some(p => route.path.startsWith(p)))

function openDropdown(name) {
  if (closeTimer) {
    clearTimeout(closeTimer)
    closeTimer = null
  }
  activeDropdown.value = name
}

function closeDropdown(name) {
  closeTimer = setTimeout(() => {
    if (activeDropdown.value === name) {
      activeDropdown.value = null
    }
  }, 150)
}

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
  background: var(--bg-primary);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 1px 0 var(--border-color), 0 4px 24px rgba(0, 0, 0, 0.3);
  padding: 0 24px;
  border-bottom: 1px solid var(--border-color);
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
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.3px;
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
}

.logo-text {
  background: var(--logo-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 2px;
  align-items: center;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 14px;
  border-radius: 8px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: -0.1px;
  cursor: pointer;
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.nav-link.active {
  color: var(--active-color);
  background: var(--active-bg);
  font-weight: 600;
}

.nav-dropdown-wrapper {
  position: relative;
}

.nav-dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  user-select: none;
}

.dropdown-arrow {
  width: 14px;
  height: 14px;
  transition: transform 0.25s ease;
  opacity: 0.5;
}

.nav-dropdown-wrapper:hover .dropdown-arrow {
  transform: rotate(180deg);
  opacity: 0.8;
}

.nav-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(-8px);
  min-width: 160px;
  background: var(--bg-card);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 6px;
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.1),
    0 12px 40px rgba(0, 0, 0, 0.4);
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  z-index: 200;
}

.nav-dropdown.visible {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
  pointer-events: auto;
}

.dropdown-item {
  display: block;
  padding: 10px 16px;
  font-size: 13px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
  letter-spacing: -0.1px;
}

.dropdown-item:hover {
  color: var(--text-primary);
  background: var(--active-bg);
}

.dropdown-item.router-link-active {
  color: var(--active-color);
  background: var(--active-bg);
}

.nav-user-link {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  text-decoration: none;
  padding: 4px 8px;
  border-radius: 6px;
}
.nav-user-link:hover { color: var(--text-primary); background: rgba(255,255,255,0.06); }
.nav-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 12px;
  padding-left: 16px;
  border-left: 1px solid var(--border-color);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--avatar-bg);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 12px rgba(var(--accent-rgb), 0.3);
}

.user-name {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: -0.1px;
}

.btn-logout {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 13px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 8px;
  cursor: pointer;
  color: #f87171;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-logout:hover {
  background: #ef4444;
  color: #fff;
  border-color: #ef4444;
  box-shadow: 0 2px 12px rgba(239, 68, 68, 0.3);
}

.btn-settings {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
}

.btn-settings:hover {
  background: var(--active-bg);
  border-color: rgba(76, 110, 245, 0.2);
  color: var(--active-color, #7c8aff);
}

.settings-icon {
  width: 16px;
  height: 16px;
}

.btn-logout:active {
  transform: scale(0.96);
}

.logout-icon {
  width: 15px;
  height: 15px;
}

@media (max-width: 960px) {
  .nav-container {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 0;
  }

  .nav-links {
    flex-wrap: wrap;
    gap: 0;
    width: 100%;
    margin-top: 8px;
  }
}
</style>