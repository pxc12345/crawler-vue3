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
            <p class="fav-url">{{ fav.targetUrl }}</p>
            <div class="fav-meta">
              <span>{{ fav.lastRun }}</span>
              <span>{{ fav.dataCount }} 条数据</span>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'

const router = useRouter()

const username = ref('Admin')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())

const totalTasks = ref(12)

const favorites = ref([
  { id: 1, name: '电商商品数据采集', targetUrl: 'https://shop.example.com', status: 'running', lastRun: '10分钟前', dataCount: 5200 },
  { id: 2, name: '竞品价格追踪', targetUrl: 'https://competitor.com', status: 'stopped', lastRun: '2小时前', dataCount: 850 },
  { id: 3, name: '新闻资讯爬取', targetUrl: 'https://news.example.com', status: 'running', lastRun: '5分钟前', dataCount: 1280 }
])

const recentTasks = ref([
  { id: 5, name: '竞品价格追踪', time: '10分钟前', action: '被修改' },
  { id: 1, name: '电商商品数据采集', time: '28分钟前', action: '数据导出' },
  { id: 3, name: '新闻资讯爬取', time: '1小时前', action: '执行完毕' },
  { id: 9, name: '金融数据采集', time: '2小时前', action: '被创建' },
  { id: 12, name: '社交媒体采集', time: '3小时前', action: '配置更新' }
])

function quickStart(fav) {
  ElMessage.success(`任务「${fav.name}」已启动`)
}
</script>

<script>
import { ElMessage } from 'element-plus'
export default { name: 'Workspace' }
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #0d1117;
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
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(124, 58, 237, 0.04), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.card {
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 24px; margin-bottom: 20px;
}
.welcome-card {
  display: flex; align-items: center; gap: 20px;
  padding: 28px 32px;
  background: linear-gradient(135deg, rgba(76,110,245,0.08), rgba(124,58,237,0.05));
  border-color: rgba(76,110,245,0.1);
}
.welcome-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; font-weight: 700; color: #fff; flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(76,110,245,0.3);
}
.welcome-info { flex: 1; }
.welcome-greeting { font-size: 22px; font-weight: 700; color: rgba(255,255,255,0.9); margin-bottom: 4px; }
.welcome-sub { font-size: 13px; color: rgba(255,255,255,0.35); }
.welcome-stats { display: flex; gap: 24px; flex-shrink: 0; }
.welcome-stat { text-align: center; }
.ws-num { display: block; font-size: 24px; font-weight: 700; color: #7c8aff; }
.ws-label { font-size: 11px; color: rgba(255,255,255,0.3); }
.section-title { font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.7); margin-bottom: 16px; }
.quick-actions { display: flex; gap: 16px; }
.quick-action {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 20px 16px; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06); border-radius: 14px;
  cursor: pointer; transition: all 0.25s ease; color: rgba(255,255,255,0.45);
}
.quick-action:hover { background: rgba(76,110,245,0.1); border-color: rgba(76,110,245,0.2); color: #7c8aff; }
.quick-action svg { width: 24px; height: 24px; }
.quick-action span { font-size: 12px; font-weight: 600; }
.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.fav-card {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px; padding: 18px;
  transition: all 0.25s ease;
}
.fav-card:hover { border-color: rgba(76,110,245,0.2); background: rgba(76,110,245,0.04); }
.fav-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.fav-star { width: 16px; height: 16px; }
.fav-status { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
.s-run { background: rgba(52,211,153,0.12); color: #34d399; }
.s-stop { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); }
.fav-name { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 4px; }
.fav-url { font-size: 11px; color: rgba(255,255,255,0.3); margin-bottom: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fav-meta { display: flex; gap: 12px; font-size: 11px; color: rgba(255,255,255,0.25); margin-bottom: 12px; }
.fav-start-btn {
  width: 100%; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 9px 14px; font-size: 12px; font-weight: 600;
  background: rgba(76,110,245,0.12); border: 1px solid rgba(76,110,245,0.2);
  border-radius: 8px; color: #7c8aff; cursor: pointer; transition: all 0.2s ease;
}
.fav-start-btn:hover { background: rgba(76,110,245,0.22); }
.fav-start-btn svg { width: 12px; height: 12px; }
.empty-state { text-align: center; padding: 40px 20px; }
.empty-icon {
  width: 64px; height: 64px; margin: 0 auto 16px;
  border-radius: 16px; background: rgba(255,255,255,0.03);
  display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.1);
}
.empty-icon svg { width: 28px; height: 28px; }
.empty-text { font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.3); margin-bottom: 4px; }
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
  background: rgba(76,110,245,0.08); display: flex; align-items: center; justify-content: center;
  color: #7c8aff; flex-shrink: 0;
}
.recent-icon svg { width: 18px; height: 18px; }
.recent-info { flex: 1; min-width: 0; }
.recent-name { display: block; font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.7); }
.recent-time { font-size: 11px; color: rgba(255,255,255,0.25); }
.recent-action-text { font-size: 11px; color: rgba(255,255,255,0.3); flex-shrink: 0; }

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