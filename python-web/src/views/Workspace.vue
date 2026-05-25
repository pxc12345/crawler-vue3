<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="welcome-card card">
        <div class="welcome-avatar">{{ userInitial }}</div>
        <div class="welcome-info">
          <h2 class="welcome-greeting">欢迎回来，{{ username }}</h2>
          <p class="welcome-sub">祝您工作顺利，今天也要加油哦 💪</p>
        </div>
        <div class="welcome-stats">
          <div class="welcome-stat">
            <span class="ws-num">{{ totalTasks }}</span>
            <span class="ws-label">总任务数</span>
          </div>
          <div class="welcome-stat">
            <span class="ws-num">{{ favorites.length }}</span>
            <span class="ws-label">收藏任务</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">快捷操作</h3>
        <div class="quick-actions">
          <div class="quick-action" @click="router.push('/tasks')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span>新建任务</span>
          </div>
          <div class="quick-action" @click="router.push('/alerts')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span>查看告警</span>
          </div>
          <div class="quick-action" @click="router.push('/data-export')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>导出数据</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">收藏任务</h3>
        <div v-if="favorites.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <p class="empty-text">暂无收藏任务</p>
          <p class="empty-desc">在任务列表中点击星标即可收藏</p>
        </div>
        <div v-else class="fav-grid">
          <div v-for="fav in favorites" :key="fav.id" class="fav-card">
            <div class="fav-top">
              <svg class="fav-star" viewBox="0 0 24 24" fill="#fbbf24" stroke="#fbbf24" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <span class="fav-status" :class="fav.status === 'running' ? 's-run' : 's-stop'">{{ fav.status === 'running' ? '运行中' : '已停止' }}</span>
            </div>
            <h4 class="fav-name">{{ fav.name }}</h4>
            <p class="fav-url">{{ fav.target_url || fav.targetUrl || '-' }}</p>
            <div class="fav-meta">
              <span>{{ fav.last_run || fav.lastRun || '-' }}</span>
              <span>{{ fav.data_count || fav.dataCount || 0 }} 条数据</span>
            </div>
            <button class="fav-start-btn" @click="quickStart(fav)">
              <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              快速启动
            </button>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">最近任务</h3>
        <div class="recent-list">
          <div v-for="(t, idx) in recentTasks" :key="idx" class="recent-item" @click="router.push('/tasks/' + t.id)">
            <div class="recent-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            </div>
            <div class="recent-info">
              <span class="recent-name">{{ t.name }}</span>
              <span class="recent-time">{{ t.time }}</span>
            </div>
            <span class="recent-action-text">{{ t.action }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { taskAPI } from '../api/task'
import { systemAPI } from '../api/system'
import NavBar from '../components/NavBar.vue'

const router = useRouter()

const username = ref('Admin')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())

const totalTasks = ref(0)

const favorites = ref([])

const recentTasks = ref([])

async function quickStart(fav) {
  try {
    await taskAPI.startTask(fav.id)
    ElMessage.success(`任务「${fav.name}」已启动`)
  } catch (error) {
    ElMessage.error('启动任务失败')
  }
}

async function fetchFavorites() {
  try {
    const res = await taskAPI.getFavorites()
    if (res.data.success) {
      favorites.value = res.data.data || []
    }
  } catch (error) {
    // 静默处理
  }
}

async function fetchRecentTasks() {
  try {
    const res = await taskAPI.getTasks({ page_size: 5 })
    if (res.data.success) {
      const list = res.data.data.list || res.data.data || []
      recentTasks.value = list.map(t => ({
        id: t.id,
        name: t.name || '未知任务',
        time: t.updated_at || t.time || '-',
        action: t.last_action || '被修改'
      }))
    }
  } catch (error) {
    // 静默处理
  }
}

async function fetchStats() {
  try {
    const res = await systemAPI.getDashboardStats()
    if (res.data.success) {
      totalTasks.value = res.data.data.total_tasks || 0
    }
  } catch (error) {
    try {
      const res = await taskAPI.getTasks({ page_size: 1 })
      if (res.data.success) {
        totalTasks.value = res.data.data.total || 0
      }
    } catch (e) {
      totalTasks.value = 0
    }
  }
}

onMounted(() => {
  fetchFavorites()
  fetchRecentTasks()
  fetchStats()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}
.page::before {
  content: '';
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(var(--accent-rgb), 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, var(--glow-color), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px; margin-bottom: 20px;
}
.welcome-card {
  display: flex; align-items: center; gap: 20px;
  padding: 28px 32px;
  background: rgba(var(--accent-rgb), 0.08);
  border-color: rgba(var(--accent-rgb), 0.1);
}
.welcome-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: var(--gradient-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; font-weight: 700; color: #fff; flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.3);
}
.welcome-info { flex: 1; }
.welcome-greeting { font-size: 22px; font-weight: 700; color: rgba(255,255,255,0.9); margin-bottom: 4px; }
.welcome-sub { font-size: 13px; color: rgba(255,255,255,0.35); }
.welcome-stats { display: flex; gap: 24px; flex-shrink: 0; }
.welcome-stat { text-align: center; }
.ws-num { display: block; font-size: 24px; font-weight: 700; color: #7c8aff; }
.ws-label { font-size: 11px; color: rgba(255,255,255,0.3); }
.section-title { font-size: 15px; font-weight: 600; color: var(--text-secondary); margin-bottom: 16px; }
.quick-actions { display: flex; gap: 16px; }
.quick-action {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 20px 16px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color); border-radius: 14px;
  cursor: pointer; transition: all 0.25s ease; color: var(--text-secondary);
}
.quick-action:hover { background: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.2); color: var(--accent-color); }
.quick-action svg { width: 24px; height: 24px; }
.quick-action span { font-size: 12px; font-weight: 600; }
.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.fav-card {
  background: rgba(255,255,255,0.03); border: 1px solid var(--border-color);
  border-radius: 14px; padding: 18px;
  transition: all 0.25s ease;
}
.fav-card:hover { border-color: rgba(var(--accent-rgb), 0.2); background: rgba(var(--accent-rgb), 0.04); }
.fav-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.fav-star { width: 16px; height: 16px; }
.fav-status { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
.s-run { background: rgba(52,211,153,0.12); color: #34d399; }
.s-stop { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); }
.fav-name { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 4px; }
.fav-url { font-size: 11px; color: var(--text-muted); margin-bottom: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fav-meta { display: flex; gap: 12px; font-size: 11px; color: var(--text-muted); margin-bottom: 12px; }
.fav-start-btn {
  width: 100%; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 9px 14px; font-size: 12px; font-weight: 600;
  background: rgba(var(--accent-rgb), 0.12); border: 1px solid rgba(var(--accent-rgb), 0.2);
  border-radius: 8px; color: var(--accent-color); cursor: pointer; transition: all 0.2s ease;
}
.fav-start-btn:hover { background: rgba(var(--accent-rgb), 0.22); }
.fav-start-btn svg { width: 12px; height: 12px; }
.empty-state { text-align: center; padding: 40px 20px; }
.empty-icon {
  width: 64px; height: 64px; margin: 0 auto 16px;
  border-radius: 16px; background: rgba(255,255,255,0.03);
  display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.1);
}
.empty-icon svg { width: 28px; height: 28px; }
.empty-text { font-size: 15px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px; }
.empty-desc { font-size: 12px; color: rgba(255,255,255,0.15); }
.recent-list { display: flex; flex-direction: column; gap: 4px; }
.recent-item {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 16px; border-radius: 10px;
  cursor: pointer; transition: all 0.2s ease;
}
.recent-item:hover { background: rgba(255,255,255,0.03); }
.recent-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: rgba(var(--accent-rgb), 0.08); display: flex; align-items: center; justify-content: center;
  color: var(--accent-color); flex-shrink: 0;
}
.recent-icon svg { width: 18px; height: 18px; }
.recent-info { flex: 1; min-width: 0; }
.recent-name { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); }
.recent-time { font-size: 11px; color: var(--text-muted); }
.recent-action-text { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .welcome-card { flex-direction: column; text-align: center; }
  .welcome-stats { gap: 16px; }
  .quick-actions { flex-direction: column; }
}
@media (max-width: 560px) {
  .fav-grid { grid-template-columns: 1fr; }
}
</style>