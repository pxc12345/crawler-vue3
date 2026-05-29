<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">代理池</h1>
        <div class="header-actions">
          <button class="btn-refresh-all" @click="refreshAll">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            全部刷新
          </button>
          <button class="btn-add" @click="showAddModal = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            添加代理
          </button>
        </div>
      </div>

      <div class="stats-row">
        <div class="card stat-card">
          <span class="stat-num available">{{ onlineCount }}</span>
          <span class="stat-label">可用IP数</span>
        </div>
        <div class="card stat-card">
          <span class="stat-num">{{ avgSuccessRate }}%</span>
          <span class="stat-label">平均成功率</span>
        </div>
        <div class="card stat-card">
          <span class="stat-num">{{ avgAliveTime }}</span>
          <span class="stat-label">平均存活时间</span>
        </div>
        <div class="card stat-card">
          <span class="stat-num available">{{ proxies.length }}</span>
          <span class="stat-label">代理总数</span>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">代理列表</h3>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>IP:端口</th>
                <th>协议</th>
                <th>状态</th>
                <th>成功率</th>
                <th>存活时间</th>
                <th>最近检查</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in proxies" :key="p.id">
                <td class="mono">{{ p.ip }}:{{ p.port }}</td>
                <td><span class="proto-tag">{{ p.protocol.toUpperCase() }}</span></td>
                <td>
                  <span class="status-dot" :class="isProxyOnline(p) ? 'dot-online' : 'dot-offline'"></span>
                  {{ isProxyOnline(p) ? '在线' : '离线' }}
                </td>
                <td>
                  <div class="success-bar">
                    <div class="success-fill" :style="{ width: proxySuccessRate(p) + '%' }" :class="proxySuccessRate(p)>=80 ? 's-high' : proxySuccessRate(p)>=50 ? 's-mid' : 's-low'"></div>
                    <span class="success-text">{{ proxySuccessRate(p) }}%</span>
                  </div>
                </td>
                <td>{{ p.alive_time || p.aliveTime || '-' }}</td>
                <td class="mono-sm">{{ p.last_check || p.lastCheck || '-' }}</td>
                <td>
                  <button class="btn-sm" @click="refreshProxy(p)">刷新</button>
                  <button class="btn-sm btn-danger-sm" @click="deleteProxy(p)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="section-header">
          <h3 class="section-title">代理分组</h3>
          <button class="btn-sm" @click="manageGroupTarget = null; newGroup = { name: '', proxies: [] }; showGroupModal = true">创建分组</button>
        </div>
        <div class="group-grid">
          <div v-for="group in groups" :key="group.id" class="group-card">
            <div class="group-header">
              <span class="group-name">{{ group.name }}</span>
              <span class="group-count">{{ (group.proxies || []).length }} 个代理</span>
            </div>
            <div class="group-proxies">
              <span v-for="pid in (group.proxies || [])" :key="pid" class="group-proxy-tag">
                {{ getProxyById(pid)?.ip || '未知' }}
              </span>
            </div>
            <div class="group-actions">
              <button class="btn-xs" @click="manageGroup(group)">管理</button>
              <button class="btn-xs btn-danger-xs" @click="deleteGroup(group)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-card">
          <h3 class="modal-title">添加代理</h3>
          <div class="form-group">
            <label class="form-label">IP 地址</label>
            <input v-model="newProxy.ip" class="input" placeholder="192.168.1.1" />
          </div>
          <div class="form-group">
            <label class="form-label">端口</label>
            <input v-model="newProxy.port" class="input" placeholder="8080" />
          </div>
          <div class="form-group">
            <label class="form-label">协议</label>
            <select v-model="newProxy.protocol" class="input input-select">
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
              <option value="socks5">SOCKS5</option>
            </select>
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showAddModal = false">取消</button>
            <button class="btn-confirm" @click="addProxy">确认添加</button>
          </div>
        </div>
      </div>

      <div v-if="showGroupModal" class="modal-overlay" @click.self="closeGroupModal">
        <div class="modal-card">
          <h3 class="modal-title">{{ manageGroupTarget ? '管理分组' : '创建分组' }}</h3>
          <div class="form-group">
            <label class="form-label">分组名称</label>
            <input v-model="newGroup.name" class="input" placeholder="高可用代理组" :disabled="!!manageGroupTarget" />
          </div>
          <div class="form-group">
            <label class="form-label">分配代理 (多选)</label>
            <p v-if="proxies.length === 0" class="proxy-check-hint">暂无代理，请先添加代理</p>
            <p v-else-if="onlineCount === 0" class="proxy-check-hint">
              当前无在线代理，仍可先分配到分组；爬虫运行时仅使用在线代理。建议点击列表「刷新」检测可用性。
            </p>
            <div class="proxy-checks">
              <label
                v-for="p in proxies"
                :key="p.id"
                class="proxy-check"
                :class="{ 'proxy-check-offline': !isProxyOnline(p) }"
              >
                <input type="checkbox" :value="Number(p.id)" v-model="newGroup.proxies" />
                <span>{{ p.ip }}:{{ p.port }}</span>
                <span class="proxy-check-status">{{ isProxyOnline(p) ? '在线' : '离线' }}</span>
              </label>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="closeGroupModal">取消</button>
            <button class="btn-confirm" @click="manageGroupTarget ? saveGroupAssignments() : createGroup()">{{ manageGroupTarget ? '保存分配' : '创建分组' }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { proxyAPI } from '../api/proxy'
import NavBar from '../components/NavBar.vue'

const showAddModal = ref(false)
const showGroupModal = ref(false)

const newProxy = ref({ ip: '', port: '', protocol: 'http' })
const newGroup = ref({ name: '', proxies: [] })

const proxies = ref([])

const groups = ref([])

function isProxyOnline(p) {
  return (p.status || '').toLowerCase() === 'online'
}

function proxySuccessRate(p) {
  const n = Number(p.success_rate ?? p.successRate ?? 0)
  return Number.isFinite(n) ? n : 0
}

const onlineCount = computed(() => proxies.value.filter(isProxyOnline).length)

const avgSuccessRate = computed(() => {
  const online = proxies.value.filter(isProxyOnline)
  if (online.length === 0) return 0
  const sum = online.reduce((s, p) => s + proxySuccessRate(p), 0)
  const avg = Math.round(sum / online.length)
  return Number.isFinite(avg) ? avg : 0
})

const avgAliveTime = computed(() => {
  const online = proxies.value.filter(isProxyOnline)
  if (online.length === 0) return '-'
  const secs = online.reduce((s, p) => s + (p.alive_seconds || 0), 0)
  const avg = Math.round(secs / online.length)
  if (avg < 60) return `${avg}秒`
  if (avg < 3600) return `${Math.round(avg / 60)}分钟`
  if (avg < 86400) return `${(avg / 3600).toFixed(1)}小时`
  return `${(avg / 86400).toFixed(1)}天`
})

function normalizeProxyIds(ids) {
  return (ids || []).map(id => Number(id)).filter(id => Number.isFinite(id))
}

function getProxyById(id) {
  const nid = Number(id)
  return proxies.value.find(p => Number(p.id) === nid)
}

async function addProxy() {
  if (!newProxy.value.ip || !newProxy.value.port) {
    ElMessage.warning('请填写完整的代理信息')
    return
  }
  try {
    const res = await proxyAPI.addProxy({
      host: newProxy.value.ip,
      ip: newProxy.value.ip,
      port: parseInt(newProxy.value.port) || 8080,
      protocol: newProxy.value.protocol
    })
    if (res.data.success) {
      newProxy.value = { ip: '', port: '', protocol: 'http' }
      showAddModal.value = false
      const probed = res.data.data?.proxy
      if (probed && isProxyOnline(probed)) {
        ElMessage.success('代理添加成功，已在线')
      } else {
        ElMessage.warning('代理已添加，但当前探测为离线（请确认 Clash 已连接后点刷新）')
      }
      await fetchProxies()
    } else {
      ElMessage.error(res.data.message || '添加失败')
    }
  } catch (error) {
    ElMessage.error('添加代理失败')
  }
}

async function refreshProxy(proxy) {
  try {
    const res = await proxyAPI.refreshProxy(proxy.id)
    if (res.data.success) {
      ElMessage.success(`代理 ${proxy.ip} 已刷新`)
      await fetchProxies()
    }
  } catch (error) {
    ElMessage.error('刷新代理失败')
  }
}

function deleteProxy(proxy) {
  ElMessageBox.confirm(`确认删除代理 ${proxy.ip}:${proxy.port}？`, '确认删除', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    try {
      await proxyAPI.deleteProxy(proxy.id)
      proxies.value = proxies.value.filter(p => p.id !== proxy.id)
      groups.value.forEach(g => {
        g.proxies = g.proxies.filter(pid => pid !== proxy.id)
      })
      ElMessage.success('代理已删除')
    } catch (error) {
      ElMessage.error('删除代理失败')
    }
  }).catch(() => {})
}

async function refreshAll() {
  try {
    for (const p of proxies.value) {
      await proxyAPI.refreshProxy(p.id)
    }
    ElMessage.success('全部代理已刷新')
    await fetchProxies()
  } catch (error) {
    ElMessage.error('刷新代理失败')
  }
}

async function createGroup() {
  if (!newGroup.value.name) {
    ElMessage.warning('请输入分组名称')
    return
  }
  try {
    const res = await proxyAPI.createProxyGroup({ name: newGroup.value.name })
    if (res.data.success) {
      const group = res.data.data || {}
      const gid = group.id || group.group_id
      if (gid) {
        await proxyAPI.syncGroupProxies(gid, normalizeProxyIds(newGroup.value.proxies))
      }
      newGroup.value = { name: '', proxies: [] }
      showGroupModal.value = false
      ElMessage.success('分组创建成功')
      await fetchGroups()
    }
  } catch (error) {
    ElMessage.error('创建分组失败')
  }
}

const manageGroupTarget = ref(null)
const manageGroupProxies = ref([])

function manageGroup(group) {
  manageGroupTarget.value = group
  const selected = normalizeProxyIds(group.proxies || [])
  manageGroupProxies.value = [...selected]
  newGroup.value = { name: group.name, proxies: [...selected] }
  showGroupModal.value = true
}

function closeGroupModal() {
  showGroupModal.value = false
  manageGroupTarget.value = null
  newGroup.value = { name: '', proxies: [] }
}

async function saveGroupAssignments() {
  if (!manageGroupTarget.value) {
    await createGroup()
    return
  }
  const gid = manageGroupTarget.value.id
  if (!gid) {
    ElMessage.error('分组 ID 无效')
    return
  }
  try {
    const res = await proxyAPI.syncGroupProxies(gid, normalizeProxyIds(newGroup.value.proxies))
    if (res.data.success) {
      closeGroupModal()
      ElMessage.success('分组已更新')
      await fetchGroups()
    } else {
      ElMessage.error(res.data.message || '更新分组失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '更新分组失败')
  }
}

function deleteGroup(group) {
  ElMessageBox.confirm(`确认删除分组「${group.name}」？`, '确认删除', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    try {
      await proxyAPI.deleteProxyGroup(group.id)
      groups.value = groups.value.filter(g => g.id !== group.id)
      ElMessage.success('分组已删除')
    } catch (error) {
      ElMessage.error('删除分组失败')
    }
  }).catch(() => {})
}

async function fetchProxies() {
  try {
    const res = await proxyAPI.getProxies({ page_size: 100 })
    if (res.data.success) {
      proxies.value = res.data.list || res.data.data?.list || res.data.data || []
    }
  } catch (error) {
    ElMessage.error('获取代理列表失败')
  }
}

async function fetchGroups() {
  try {
    const res = await proxyAPI.getProxyGroups()
    if (res.data.success) {
      groups.value = (res.data.data || []).map(g => ({
        ...g,
        proxies: normalizeProxyIds(g.proxies || [])
      }))
    }
  } catch (error) {
    // 静默处理
  }
}

onMounted(() => {
  fetchProxies()
  fetchGroups()
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
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(124, 58, 237, 0.04), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  color: var(--text-primary); letter-spacing: -0.5px;
}
.header-actions { display: flex; gap: 10px; }
.btn-refresh-all {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 18px; font-size: 13px; font-weight: 500;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease;
}
.btn-refresh-all:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }
.btn-refresh-all svg { width: 15px; height: 15px; }
.btn-add {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 18px; font-size: 13px; font-weight: 600;
  background: var(--gradient-primary);
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease; box-shadow: 0 2px 12px rgba(var(--accent-rgb), 0.3);
}
.btn-add:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.45); }
.btn-add svg { width: 16px; height: 16px; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px; margin-bottom: 20px;
}
.stat-card { padding: 20px; text-align: center; }
.stat-num { display: block; font-size: 28px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.stat-num.available { color: #34d399; }
.stat-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.section-title { font-size: 15px; font-weight: 600; color: var(--text-secondary); margin-bottom: 16px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-header .section-title { margin-bottom: 0; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  padding: 12px 14px; text-align: left; font-weight: 600;
  color: var(--text-muted); font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid var(--border-color);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table td {
  padding: 12px 14px; color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}
.data-table tbody tr:hover { background: rgba(var(--accent-rgb), 0.04); }
.mono { font-family: monospace; font-size: 13px; }
.mono-sm { font-family: monospace; font-size: 11px; color: var(--text-muted); }
.proto-tag {
  padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;
  background: rgba(var(--accent-rgb), 0.12); color: var(--accent-color);
}
.status-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px;
}
.dot-online { background: #34d399; box-shadow: 0 0 6px rgba(52,211,153,0.4); }
.dot-offline { background: #f87171; }
.success-bar {
  display: flex; align-items: center; gap: 8px;
  height: 18px; background: rgba(255,255,255,0.04);
  border-radius: 5px; overflow: hidden; min-width: 80px; position: relative;
}
.success-fill { height: 100%; border-radius: 5px; transition: width 0.5s ease; }
.s-high { background: #34d399; }
.s-mid { background: #fbbf24; }
.s-low { background: #f87171; }
.success-text { position: absolute; right: 6px; font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.5); }
.btn-sm {
  padding: 4px 10px; font-size: 11px; font-weight: 500;
  background: rgba(var(--accent-rgb), 0.1); border: 1px solid rgba(var(--accent-rgb), 0.15);
  border-radius: 6px; color: var(--accent-color); cursor: pointer; transition: all 0.2s ease;
  margin-right: 4px;
}
.btn-sm:hover { background: rgba(var(--accent-rgb), 0.2); }
.btn-danger-sm { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.15); color: #f87171; }
.btn-danger-sm:hover { background: rgba(239,68,68,0.2); }
.btn-xs { padding: 4px 8px; font-size: 10px; font-weight: 500; background: rgba(76,110,245,0.1); border: 1px solid rgba(76,110,245,0.15); border-radius: 5px; color: #7c8aff; cursor: pointer; transition: all 0.2s ease; margin-right: 4px; }
.btn-xs:hover { background: rgba(76,110,245,0.2); }
.btn-danger-xs { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.15); color: #f87171; }
.btn-danger-xs:hover { background: rgba(239,68,68,0.2); }
.group-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.group-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: 12px; padding: 16px;
}
.group-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.group-name { font-size: 14px; font-weight: 600; color: var(--text-secondary); }
.group-count { font-size: 11px; color: var(--text-muted); }
.group-proxies { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.group-proxy-tag {
  padding: 2px 7px; font-size: 10px; font-family: monospace;
  background: rgba(var(--accent-rgb), 0.08); color: var(--text-muted);
  border-radius: 4px;
}
.group-actions { display: flex; gap: 6px; }
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal-card {
  background: var(--bg-card);
  backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  border-radius: 20px; padding: 32px; min-width: 420px;
  box-shadow: 0 16px 64px rgba(0,0,0,0.5);
}
.modal-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 24px; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 12px; font-weight: 500; color: var(--text-muted); margin-bottom: 6px; }
.input {
  width: 100%; padding: 9px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-primary);
  outline: none; transition: all 0.2s ease; box-sizing: border-box;
}
.input:focus { border-color: rgba(var(--accent-rgb), 0.4); background: rgba(255, 255, 255, 0.06); }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
.btn-cancel {
  padding: 10px 22px; font-size: 13px; font-weight: 500;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease;
}
.btn-cancel:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }
.btn-confirm {
  padding: 10px 22px; font-size: 13px; font-weight: 600;
  background: var(--gradient-primary);
  border: none; border-radius: 10px; color: #fff; cursor: pointer; transition: all 0.25s ease;
  box-shadow: 0 2px 12px rgba(var(--accent-rgb), 0.3);
}
.btn-confirm:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.45); }
.proxy-checks { max-height: 180px; overflow-y: auto; display: flex; flex-wrap: wrap; gap: 6px; }
.proxy-check {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 10px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px; font-size: 12px; color: var(--text-secondary); cursor: pointer;
}
.proxy-check input { accent-color: #4c6ef5; }
.proxy-check-hint {
  font-size: 12px; color: var(--text-muted); margin-bottom: 8px; line-height: 1.5;
}
.proxy-check-offline { opacity: 0.75; }
.proxy-check-status {
  font-size: 10px; padding: 1px 6px; border-radius: 4px;
  background: rgba(255,255,255,0.06); color: var(--text-muted);
}

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .modal-card { min-width: auto; width: 90%; padding: 24px; }
}
@media (max-width: 560px) {
  .stats-row { grid-template-columns: 1fr; }
  .header-actions { flex-direction: column; }
}
</style>