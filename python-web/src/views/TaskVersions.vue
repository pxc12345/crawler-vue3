<template>
  <div class="versions-page">
    <NavBar />
    <div class="versions-content">
      <div class="detail-header">
        <button class="btn-back" @click="$router.push(`/tasks/${$route.params.id}`)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <div class="header-info">
          <h1 class="detail-title">版本历史 - {{ taskName }}</h1>
          <span class="version-count">{{ versions.length }} 个版本</span>
        </div>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 5" :key="n" class="skeleton-item">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40"></div>
        </div>
      </div>

      <div v-else-if="versions.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <line x1="6" y1="3" x2="6" y2="15"/>
            <circle cx="18" cy="6" r="3"/>
            <circle cx="6" cy="18" r="3"/>
            <path d="M18 9a9 9 0 0 1-9 9"/>
          </svg>
        </div>
        <p class="empty-text">暂无版本记录</p>
        <p class="empty-desc">每次修改任务配置后会自动保存版本</p>
      </div>

      <div v-else class="version-timeline">
        <div
          v-for="(ver, idx) in versions"
          :key="ver.id"
          class="version-card"
          :class="{ current: ver.isCurrent }"
        >
          <div class="version-badge">
            <div class="version-dot" :class="{ active: ver.isCurrent }"></div>
            <div class="version-line" v-if="idx < versions.length - 1"></div>
          </div>

          <div class="version-body">
            <div class="version-header">
              <div class="version-header-left">
                <span class="version-number">v{{ ver.version }}</span>
                <span v-if="ver.isCurrent" class="current-badge">当前版本</span>
              </div>
              <span class="version-time">{{ ver.time }}</span>
            </div>

            <div class="version-changelog">
              <h4 class="changelog-title">变更记录</h4>
              <ul class="changelog-list">
                <li v-for="(change, ci) in ver.changes" :key="ci">{{ change }}</li>
              </ul>
            </div>

            <div class="version-meta">
              <div class="version-meta-item">
                <span class="meta-label">修改人</span>
                <span class="meta-value">{{ ver.author }}</span>
              </div>
              <div class="version-meta-item">
                <span class="meta-label">配置快照</span>
                <span class="meta-value">Cron: {{ ver.cron }} | 并发: {{ ver.concurrency }} | 间隔: {{ ver.interval }}ms</span>
              </div>
            </div>

            <div class="version-actions">
              <button
                v-if="!ver.isCurrent"
                class="ver-btn primary"
                @click="rollbackVersion(ver)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="1 4 1 10 7 10"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
                回滚到此版本
              </button>
              <button class="ver-btn" @click="toggleCompare(ver)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="20" x2="18" y2="10"/>
                  <line x1="12" y1="20" x2="12" y2="4"/>
                  <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
                {{ comparedVersions.includes(ver.id) ? '取消对比' : '对比' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="comparedVersions.length === 2" class="compare-panel">
        <h3 class="compare-title">版本对比</h3>
        <div class="compare-table">
          <div class="compare-row header">
            <span class="compare-col">配置项</span>
            <span class="compare-col">v{{ compareOld.version }}</span>
            <span class="compare-col">v{{ compareNew.version }}</span>
          </div>
          <div class="compare-row">
            <span class="compare-col label">任务名称</span>
            <span class="compare-col">{{ compareOld.name }}</span>
            <span class="compare-col changed">{{ compareNew.name }}</span>
          </div>
          <div class="compare-row">
            <span class="compare-col label">Cron</span>
            <span class="compare-col">{{ compareOld.cron }}</span>
            <span class="compare-col changed">{{ compareNew.cron }}</span>
          </div>
          <div class="compare-row">
            <span class="compare-col label">并发数</span>
            <span class="compare-col">{{ compareOld.concurrency }}</span>
            <span class="compare-col changed">{{ compareNew.concurrency }}</span>
          </div>
          <div class="compare-row">
            <span class="compare-col label">请求间隔</span>
            <span class="compare-col">{{ compareOld.interval }}ms</span>
            <span class="compare-col changed">{{ compareNew.interval }}ms</span>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showRollbackModal" class="modal-overlay" @click.self="showRollbackModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h2 class="modal-title">确认回滚</h2>
            <button class="modal-close" @click="showRollbackModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <p class="rollback-warning">
              您确定要将任务「{{ taskName }}」回滚到版本
              <strong>v{{ rollbackTarget?.version }}</strong> 吗？
            </p>
            <p class="rollback-note">
              回滚操作将覆盖当前配置，但不会影响已有的数据采集结果。
              此操作会生成一个新的版本记录。
            </p>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="showRollbackModal = false">取消</button>
            <button class="modal-btn danger" @click="confirmRollback">确认回滚</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const taskName = ref('')
const showRollbackModal = ref(false)
const rollbackTarget = ref(null)
const comparedVersions = ref([])

const versions = ref([])

const compareOld = computed(() => {
  if (comparedVersions.value.length === 2) {
    const ids = [...comparedVersions.value].sort((a, b) => a - b)
    return versions.value.find(v => v.id === ids[0]) || {}
  }
  return {}
})

const compareNew = computed(() => {
  if (comparedVersions.value.length === 2) {
    const ids = [...comparedVersions.value].sort((a, b) => a - b)
    return versions.value.find(v => v.id === ids[1]) || {}
  }
  return {}
})

function rollbackVersion(ver) {
  rollbackTarget.value = ver
  showRollbackModal.value = true
}

async function confirmRollback() {
  if (!rollbackTarget.value) return
  try {
    const res = await taskAPI.rollbackVersion(route.params.id, rollbackTarget.value.id)
    if (res.data.success) {
      ElMessage.success('回滚成功')
      showRollbackModal.value = false
      rollbackTarget.value = null
      fetchVersions()
    } else {
      ElMessage.error(res.data.message || '回滚失败')
    }
  } catch (e) {
    ElMessage.error('回滚失败')
  }
}

function toggleCompare(ver) {
  const idx = comparedVersions.value.indexOf(ver.id)
  if (idx !== -1) {
    comparedVersions.value = comparedVersions.value.filter(id => id !== ver.id)
  } else {
    if (comparedVersions.value.length >= 2) {
      comparedVersions.value.shift()
    }
    comparedVersions.value.push(ver.id)
  }
}

function mapVersionFromApi(item, maxVersionIndex) {
  let config = item.config
  if (typeof config === 'string') {
    try { config = JSON.parse(config) } catch (e) { config = {} }
  }
  config = config || {}
  let changes = []
  if (item.change_log) {
    if (typeof item.change_log === 'string') {
      changes = item.change_log.split('\n').filter(c => c.trim())
    } else {
      changes = Array.isArray(item.change_log) ? item.change_log : [item.change_log]
    }
  }
  return {
    id: item.id,
    version: item.version_index,
    isCurrent: item.version_index === maxVersionIndex,
    time: item.created_at || '',
    author: item.author || '',
    cron: config.cron_expr || config.cron || '',
    concurrency: config.concurrency || 0,
    interval: config.interval || 0,
    name: config.name || '',
    changes: changes
  }
}

async function fetchTaskName() {
  try {
    const res = await taskAPI.getTask(route.params.id)
    if (res.data.success && res.data.data) {
      taskName.value = res.data.data.name || ''
    }
  } catch (e) {
    // silent
  }
}

async function fetchVersions() {
  loading.value = true
  try {
    const res = await taskAPI.getVersions(route.params.id)
    if (res.data.success) {
      const data = res.data.data || []
      const maxVersion = data.reduce((max, v) => Math.max(max, v.version_index || 0), 0)
      versions.value = data.map(item => mapVersionFromApi(item, maxVersion))
    } else {
      ElMessage.error(res.data.message || '获取版本列表失败')
      versions.value = []
    }
  } catch (e) {
    ElMessage.error('获取版本列表失败')
    versions.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTaskName()
  fetchVersions()
})
</script>

<style scoped>
.versions-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}

.versions-page::before {
  content: '';
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16, 185, 129, 0.04), transparent);
  pointer-events: none; z-index: 0;
}

.versions-content {
  max-width: 800px; margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}

.detail-header {
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 36px;
}

.btn-back {
  width: 42px; height: 42px; display: flex; align-items: center; justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.25s ease; flex-shrink: 0;
}

.btn-back:hover { color: var(--text-primary); border-color: rgba(255, 255, 255, 0.15); }
.btn-back svg { width: 20px; height: 20px; }

.header-info { flex: 1; }

.detail-title {
  font-size: 22px; font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px; letter-spacing: -0.4px;
}

.version-count {
  font-size: 13px; color: var(--text-muted);
}

.skeleton-list { display: flex; flex-direction: column; gap: 16px; }
.skeleton-item {
  background: var(--bg-card); border-radius: 16px;
  padding: 28px; border: 1px solid var(--border-color);
}
.skeleton-line {
  height: 14px; background: rgba(255, 255, 255, 0.04);
  border-radius: 7px; margin-bottom: 10px;
  animation: shimmer 1.5s ease-in-out infinite;
}
.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }
@keyframes shimmer { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.8; } }

.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon {
  width: 80px; height: 80px; margin: 0 auto 24px;
  border-radius: 20px; background: rgba(255, 255, 255, 0.03);
  display: flex; align-items: center; justify-content: center;
  color: rgba(255, 255, 255, 0.1);
}
.empty-icon svg { width: 36px; height: 36px; }
.empty-text { font-size: 18px; font-weight: 600; color: rgba(255, 255, 255, 0.35); margin-bottom: 8px; }
.empty-desc { font-size: 13px; color: rgba(255, 255, 255, 0.2); }

.version-timeline {
  display: flex; flex-direction: column;
}

.version-card {
  display: flex; gap: 0;
  position: relative;
}

.version-badge {
  display: flex; flex-direction: column; align-items: center;
  width: 36px; flex-shrink: 0; padding-top: 22px;
}

.version-dot {
  width: 12px; height: 12px; border-radius: 50%;
  border: 2px solid var(--border-color);
  background: var(--bg-primary); z-index: 1;
  transition: all 0.3s ease;
}

.version-dot.active {
  border-color: var(--accent-color); background: var(--accent-color);
  box-shadow: 0 0 12px var(--glow-color);
}

.version-line {
  width: 2px; flex: 1; min-height: 20px;
  background: var(--border-color);
}

.version-body {
  flex: 1; min-width: 0;
  background: var(--bg-card);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px; padding: 20px 22px;
  margin-bottom: 16px; margin-left: 12px;
  transition: all 0.3s ease;
}

.version-card.current .version-body {
  border-color: rgba(var(--accent-rgb), 0.2);
  background: var(--bg-card);
}

.version-body:hover {
  border-color: var(--border-color);
  background: var(--bg-card);
}

.version-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px;
}

.version-header-left {
  display: flex; align-items: center; gap: 10px;
}

.version-number {
  font-size: 16px; font-weight: 800;
  color: var(--text-primary);
}

.current-badge {
  font-size: 10px; font-weight: 700; padding: 3px 10px;
  background: rgba(var(--accent-rgb), 0.15); color: var(--accent-color);
  border-radius: 10px;
}

.version-time {
  font-size: 12px; color: var(--text-muted);
}

.version-changelog {
  margin-bottom: 14px;
}

.changelog-title {
  font-size: 11px; font-weight: 600;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase; letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.changelog-list {
  list-style: none; padding: 0;
}

.changelog-list li {
  font-size: 12px; color: var(--text-secondary);
  padding: 3px 0; padding-left: 16px; position: relative;
}

.changelog-list li::before {
  content: ''; position: absolute; left: 0; top: 10px;
  width: 5px; height: 5px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.version-meta {
  display: flex; flex-direction: column; gap: 6px;
  padding: 12px 0; border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 14px;
}

.version-meta-item {
  display: flex; gap: 10px; font-size: 12px;
}

.meta-label {
  color: var(--text-muted); flex-shrink: 0;
}

.meta-value {
  color: var(--text-secondary);
}

.version-actions {
  display: flex; gap: 8px;
}

.ver-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 7px 14px; font-size: 12px; font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.2s ease;
}

.ver-btn svg { width: 14px; height: 14px; }

.ver-btn:hover { color: var(--text-primary); background: rgba(255, 255, 255, 0.08); }

.ver-btn.primary {
  background: var(--gradient-primary);
  color: #fff; border: none;
  box-shadow: 0 2px 10px rgba(var(--accent-rgb), 0.25);
}

.ver-btn.primary:hover {
  box-shadow: 0 4px 16px rgba(var(--accent-rgb), 0.4);
  transform: translateY(-1px);
}

.compare-panel {
  margin-top: 28px;
  background: var(--bg-card);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px; padding: 24px;
}

.compare-title {
  font-size: 16px; font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.compare-table {
  border-radius: 10px; overflow: hidden;
  border: 1px solid var(--border-color);
}

.compare-row {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  border-bottom: 1px solid var(--border-color);
}

.compare-row:last-child { border-bottom: none; }
.compare-row.header { background: rgba(255, 255, 255, 0.03); }

.compare-col {
  padding: 10px 16px; font-size: 12px;
  color: var(--text-secondary);
}

.compare-col.label { color: var(--text-secondary); font-weight: 600; }
.compare-col.changed { color: #fbbf24; font-weight: 600; }
.compare-row.header .compare-col { font-weight: 700; color: var(--text-secondary); }

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--bg-card);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  border-radius: 18px; width: 460px; max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalIn 0.3s cubic-bezier(0.22, 0.61, 0.36, 1);
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 22px 24px; border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: 18px; font-weight: 700;
  color: var(--text-primary);
}

.modal-close {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  background: transparent; border: none;
  color: var(--text-secondary); font-size: 22px;
  cursor: pointer; border-radius: 8px; transition: all 0.2s ease;
}

.modal-close:hover { color: var(--text-primary); background: rgba(255, 255, 255, 0.05); }

.modal-body { padding: 24px; }

.rollback-warning {
  font-size: 14px; color: var(--text-primary);
  margin-bottom: 12px; line-height: 1.5;
}

.rollback-warning strong { color: #fbbf24; }

.rollback-note {
  font-size: 12px; color: var(--text-muted);
  line-height: 1.5;
}

.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 20px 24px; border-top: 1px solid var(--border-color);
}

.modal-btn {
  padding: 10px 22px; font-size: 13px; font-weight: 600;
  border-radius: 10px; cursor: pointer; transition: all 0.25s ease;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary);
}

.modal-btn:hover { background: rgba(255, 255, 255, 0.08); color: var(--text-primary); }

.modal-btn.danger {
  background: rgba(239, 68, 68, 0.15); color: #f87171;
  border-color: rgba(239, 68, 68, 0.2);
}

.modal-btn.danger:hover { background: rgba(239, 68, 68, 0.25); }

@media (max-width: 768px) {
  .versions-content { padding: 24px 16px 64px; }
  .detail-title { font-size: 20px; }
  .compare-row { grid-template-columns: 1fr 1fr 1fr; }
  .compare-col { font-size: 11px; padding: 8px 10px; }
}
</style>