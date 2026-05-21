<template>
  <div class="home-page">
    <NavBar />
    <div class="home-content">
      <div class="welcome-section">
        <div class="welcome-card">
          <div class="welcome-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <h1 class="welcome-title">欢迎回来，{{ authStore.user?.username }}</h1>
          <p class="welcome-subtitle">今天是美好的一天，开始您的管理工作吧</p>
          <div class="welcome-time">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>{{ greeting }}</span>
          </div>
        </div>
      </div>

      <div class="feature-grid">
        <div class="feature-card card-crawler" @click="$router.push('/crawler')">
          <div class="feature-icon crawler-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
              <path d="M11 8v6"/>
              <path d="M8 11h6"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">爬虫管理</h3>
            <p class="feature-desc">管理和监控数据采集任务，实时追踪爬取状态</p>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
            </svg>
          </div>
        </div>

        <div class="feature-card card-stats">
          <div class="feature-icon stats-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">今日统计</h3>
            <p class="feature-desc">查看今日数据概览：采集量、活跃任务、系统状态</p>
          </div>
          <div class="feature-stats-preview">
            <div class="stat-item">
              <span class="stat-value">128</span>
              <span class="stat-label">采集</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">6</span>
              <span class="stat-label">任务</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value on">正常</span>
              <span class="stat-label">状态</span>
            </div>
          </div>
        </div>

        <div class="feature-card card-actions">
          <div class="feature-icon actions-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">快捷操作</h3>
            <p class="feature-desc">一键执行常用功能，提升工作效率</p>
          </div>
          <div class="feature-quick-links">
            <span class="quick-link">新建任务</span>
            <span class="quick-link">数据导出</span>
          </div>
        </div>

        <div class="feature-card card-notice">
          <div class="feature-icon notice-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">系统通知</h3>
            <p class="feature-desc">查看最新系统消息和告警通知</p>
          </div>
          <div class="feature-notice-badge">3 条新消息</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import NavBar from '../components/NavBar.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loaded = ref(false)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了，注意休息'
  if (hour < 11) return '上午好，精力充沛的一天'
  if (hour < 14) return '中午好，别忘了休息一下'
  if (hour < 18) return '下午好，继续加油'
  return '晚上好，回顾一下今天的成果'
})

onMounted(() => {
  setTimeout(() => {
    loaded.value = true
  }, 100)
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #0d1117;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
  position: relative;
}

.home-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16, 185, 129, 0.05), transparent);
  pointer-events: none;
  z-index: 0;
}

.home-content {
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px 80px;
  position: relative;
  z-index: 1;
}

.welcome-section {
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px;
  padding: 48px 48px 40px;
  text-align: center;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.5);
  position: relative;
  overflow: hidden;
}

.welcome-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-700), #6366f1, var(--primary-500));
}

.welcome-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, var(--primary-50), var(--primary-100));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-600);
}

.welcome-icon svg {
  width: 30px;
  height: 30px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--gray-800);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 15px;
  color: var(--gray-500);
  margin-bottom: 20px;
}

.welcome-time {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: var(--gray-50);
  border-radius: 20px;
  font-size: 13px;
  color: var(--gray-500);
  font-weight: 500;
}

.welcome-time svg {
  width: 16px;
  height: 16px;
  color: var(--primary-500);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 28px 24px 24px;
  transition: all 0.35s cubic-bezier(0.22, 0.61, 0.36, 1);
  cursor: default;
  position: relative;
  overflow: hidden;
  opacity: 0;
  transform: translateY(24px);
}

.feature-card:nth-child(1) { animation: fadeInUp 0.5s 0.15s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }
.feature-card:nth-child(2) { animation: fadeInUp 0.5s 0.25s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }
.feature-card:nth-child(3) { animation: fadeInUp 0.5s 0.35s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }
.feature-card:nth-child(4) { animation: fadeInUp 0.5s 0.45s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }

.feature-card:hover {
  transform: translateY(-6px);
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.14);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.08),
    0 12px 40px rgba(0, 0, 0, 0.2);
}

.card-crawler {
  cursor: pointer;
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}

.feature-icon svg {
  width: 22px;
  height: 22px;
}

.crawler-icon {
  background: rgba(99, 102, 241, 0.14);
  color: #818cf8;
}

.stats-icon {
  background: rgba(16, 185, 129, 0.14);
  color: #34d399;
}

.actions-icon {
  background: rgba(245, 158, 11, 0.14);
  color: #fbbf24;
}

.notice-icon {
  background: rgba(239, 68, 68, 0.14);
  color: #f87171;
}

.feature-info {
  margin-bottom: 16px;
}

.feature-title {
  font-size: 16px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 6px;
  letter-spacing: -0.2px;
}

.feature-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.5;
}

.feature-arrow {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: rgba(255, 255, 255, 0.25);
  transition: all 0.3s ease;
}

.feature-arrow svg {
  width: 18px;
  height: 18px;
}

.card-crawler:hover .feature-arrow {
  color: #818cf8;
  transform: translateX(4px);
}

.feature-stats-preview {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 12px 0 0;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: -0.5px;
}

.stat-value.on {
  font-size: 14px;
  color: #34d399;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.06);
}

.feature-quick-links {
  display: flex;
  gap: 8px;
  padding-top: 4px;
}

.quick-link {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  border: 1px solid transparent;
}

.quick-link:hover {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.2);
}

.feature-notice-badge {
  display: inline-flex;
  padding: 6px 14px;
  background: rgba(239, 68, 68, 0.12);
  border-radius: 20px;
  font-size: 12px;
  color: #f87171;
  font-weight: 600;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .welcome-card {
    padding: 36px 28px 32px;
  }

  .welcome-title {
    font-size: 24px;
  }
}

@media (max-width: 560px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }

  .home-content {
    padding: 32px 16px 64px;
  }

  .welcome-card {
    padding: 28px 20px 24px;
  }

  .welcome-title {
    font-size: 20px;
  }
}
</style>