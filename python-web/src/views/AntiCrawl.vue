<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">风控配置</h1>
      </div>

      <div class="card tabs-wrapper">
        <div class="tabs">
          <button class="tab" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">黑白名单</button>
          <button class="tab" :class="{ active: activeTab === 'freq' }" @click="activeTab = 'freq'">请求频率控制</button>
        </div>
      </div>

      <div v-if="activeTab === 'list'" class="tab-content">
        <div class="two-col">
          <div class="card col-card">
            <div class="col-header black">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
              <h3>黑名单</h3>
              <span class="col-count">{{ blacklist.length }}</span>
            </div>
            <div class="add-row">
              <input v-model="blackInput.url" class="input" placeholder="输入URL..." />
              <input v-model="blackInput.reason" class="input" placeholder="原因(可选)" />
              <button class="btn-add-small" @click="addBlack">添加</button>
            </div>
            <div class="list-items">
              <div v-for="item in blacklist" :key="item.id || item.url" class="list-item item-black">
                <div class="item-info">
                  <span class="item-url">{{ item.url }}</span>
                  <span class="item-reason" v-if="item.reason">{{ item.reason }}</span>
                </div>
                <button class="btn-remove" @click="removeBlack(item)">×</button>
              </div>
              <div v-if="blacklist.length === 0" class="list-empty">黑名单为空</div>
            </div>
          </div>

          <div class="card col-card">
            <div class="col-header white">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <h3>白名单</h3>
              <span class="col-count white-count">{{ whitelist.length }}</span>
            </div>
            <div class="add-row">
              <input v-model="whiteInput.url" class="input" placeholder="输入URL..." />
              <input v-model="whiteInput.reason" class="input" placeholder="原因(可选)" />
              <button class="btn-add-small green" @click="addWhite">添加</button>
            </div>
            <div class="list-items">
              <div v-for="item in whitelist" :key="item.id || item.url" class="list-item item-white">
                <div class="item-info">
                  <span class="item-url">{{ item.url }}</span>
                  <span class="item-reason" v-if="item.reason">{{ item.reason }}</span>
                </div>
                <button class="btn-remove" @click="removeWhite(item)">×</button>
              </div>
              <div v-if="whitelist.length === 0" class="list-empty">白名单为空</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'freq'" class="tab-content">
        <div class="card">
          <h3 class="section-title">全局频率设置</h3>
          <div class="freq-config">
            <div class="freq-row">
              <label class="freq-label">每分钟最大请求数</label>
              <div class="slider-group">
                <input type="range" v-model.number="globalRpm" min="10" max="200" class="slider" />
                <span class="slider-val">{{ globalRpm }}</span>
              </div>
            </div>
            <div class="freq-row">
              <label class="freq-label">最大并发连接数</label>
              <div class="slider-group">
                <input type="range" v-model.number="globalConcurrent" min="1" max="50" class="slider" />
                <span class="slider-val">{{ globalConcurrent }}</span>
              </div>
            </div>
            <button class="btn-save-freq" @click="saveGlobalFreq">保存全局设置</button>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title">按任务配置</h3>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>任务名称</th>
                  <th>请求/分钟</th>
                  <th>最大并发</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in taskFreqs" :key="t.name">
                  <td class="task-name">{{ t.name }}</td>
                  <td>{{ t.rpm }}</td>
                  <td>{{ t.concurrent }}</td>
                  <td><button class="btn-sm" @click="editTaskFreq(t)">编辑</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="showTaskEdit" class="modal-overlay" @click.self="showTaskEdit = false">
        <div class="modal-card">
          <h3 class="modal-title">编辑任务频率 - {{ editingTask?.name }}</h3>
          <div class="form-group">
            <label class="form-label">每分钟请求数</label>
            <input type="number" v-model.number="editRpm" class="input" min="1" max="200" />
          </div>
          <div class="form-group">
            <label class="form-label">最大并发连接数</label>
            <input type="number" v-model.number="editConcurrent" class="input" min="1" max="50" />
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showTaskEdit = false">取消</button>
            <button class="btn-confirm" @click="saveTaskFreq">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { proxyAPI } from '../api/proxy'
import NavBar from '../components/NavBar.vue'

const activeTab = ref('list')
const showTaskEdit = ref(false)
const editingTask = ref(null)
const editRpm = ref(60)
const editConcurrent = ref(5)

const globalRpm = ref(100)
const globalConcurrent = ref(10)

const blackInput = ref({ url: '', reason: '' })
const whiteInput = ref({ url: '', reason: '' })

const blacklist = ref([])

const whitelist = ref([])

const taskFreqs = ref([])

async function addBlack() {
  if (!blackInput.value.url) { ElMessage.warning('请输入URL'); return }
  try {
    const res = await proxyAPI.addBlacklist({ url: blackInput.value.url, reason: blackInput.value.reason })
    if (res.data.success) {
      blackInput.value = { url: '', reason: '' }
      ElMessage.success('已添加到黑名单')
      await fetchBlacklist()
    }
  } catch (error) {
    ElMessage.error('添加黑名单失败')
  }
}

async function removeBlack(item) {
  try {
    await proxyAPI.removeBlacklist(item.id || item.url)
    blacklist.value = blacklist.value.filter(b => (b.id || b.url) !== (item.id || item.url))
    ElMessage.success('已从黑名单移除')
  } catch (error) {
    ElMessage.error('移除黑名单失败')
  }
}

async function addWhite() {
  if (!whiteInput.value.url) { ElMessage.warning('请输入URL'); return }
  try {
    const res = await proxyAPI.addWhitelist({ url: whiteInput.value.url, reason: whiteInput.value.reason })
    if (res.data.success) {
      whiteInput.value = { url: '', reason: '' }
      ElMessage.success('已添加到白名单')
      await fetchWhitelist()
    }
  } catch (error) {
    ElMessage.error('添加白名单失败')
  }
}

async function removeWhite(item) {
  try {
    await proxyAPI.removeWhitelist(item.id || item.url)
    whitelist.value = whitelist.value.filter(w => (w.id || w.url) !== (item.id || item.url))
    ElMessage.success('已从白名单移除')
  } catch (error) {
    ElMessage.error('移除白名单失败')
  }
}

async function saveGlobalFreq() {
  try {
    await proxyAPI.setRateLimit({
      task_id: null,
      requests_per_minute: globalRpm.value,
      concurrent_max: globalConcurrent.value
    })
    ElMessage.success('全局频率设置已保存')
  } catch (error) {
    ElMessage.error('保存频率设置失败')
  }
}

function editTaskFreq(task) {
  editingTask.value = task
  editRpm.value = task.requests_per_minute || task.rpm || 60
  editConcurrent.value = task.concurrent_max || task.concurrent || 5
  showTaskEdit.value = true
}

async function saveTaskFreq() {
  if (editingTask.value) {
    try {
      const taskId = editingTask.value.id || editingTask.value.task_id
      await proxyAPI.setRateLimit({
        task_id: taskId,
        requests_per_minute: editRpm.value,
        concurrent_max: editConcurrent.value
      })
      editingTask.value.requests_per_minute = editRpm.value
      editingTask.value.concurrent_max = editConcurrent.value
      editingTask.value.rpm = editRpm.value
      editingTask.value.concurrent = editConcurrent.value
      showTaskEdit.value = false
      ElMessage.success('任务频率设置已保存')
    } catch (error) {
      ElMessage.error('保存任务频率失败')
    }
  }
}

async function fetchBlacklist() {
  try {
    const res = await proxyAPI.getBlacklist()
    if (res.data.success) {
      blacklist.value = res.data.data || []
    }
  } catch (error) {
    // 静默处理
  }
}

async function fetchWhitelist() {
  try {
    const res = await proxyAPI.getWhitelist()
    if (res.data.success) {
      whitelist.value = res.data.data || []
    }
  } catch (error) {
    // 静默处理
  }
}

async function fetchRateLimits() {
  try {
    const res = await proxyAPI.getRateLimits()
    if (res.data.success) {
      const data = res.data.data || []
      taskFreqs.value = data.map(t => ({
        id: t.id || t.task_id,
        name: t.name || t.task_name || t.task_id,
        rpm: t.requests_per_minute || t.rpm || 0,
        concurrent: t.concurrent_max || t.concurrent || 0,
        requests_per_minute: t.requests_per_minute,
        concurrent_max: t.concurrent_max
      }))
    }
  } catch (error) {
    // 静默处理
  }
}

onMounted(() => {
  fetchBlacklist()
  fetchWhitelist()
  fetchRateLimits()
})
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
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;
}
.card {
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 24px; margin-bottom: 20px;
}
.tabs-wrapper { padding: 4px; margin-bottom: 20px; }
.tabs { display: flex; gap: 4px; }
.tab {
  flex: 1; padding: 11px 20px; font-size: 13px; font-weight: 600;
  color: rgba(255,255,255,0.4); background: transparent; border: none;
  border-radius: 13px; cursor: pointer; transition: all 0.2s ease;
}
.tab:hover { color: rgba(255,255,255,0.65); }
.tab.active { background: rgba(76,110,245,0.12); color: #7c8aff; }
.tab-content { animation: fadeIn 0.25s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.col-card { padding: 20px; }
.col-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 16px;
  font-size: 15px; font-weight: 700;
}
.col-header svg { width: 20px; height: 20px; }
.col-header.black { color: #f87171; }
.col-header.white { color: #34d399; }
.col-count {
  margin-left: auto; padding: 2px 10px; border-radius: 10px;
  font-size: 11px; font-weight: 600;
}
.col-header.black .col-count { background: rgba(248,113,113,0.12); color: #f87171; }
.col-count.white-count { background: rgba(52,211,153,0.12); color: #34d399; }
.add-row { display: flex; gap: 6px; margin-bottom: 14px; }
.input {
  flex: 1; padding: 8px 12px; font-size: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px; color: rgba(255, 255, 255, 0.75);
  outline: none; transition: all 0.2s ease; min-width: 0;
}
.input:focus { border-color: rgba(76, 110, 245, 0.4); background: rgba(255, 255, 255, 0.06); }
.btn-add-small {
  padding: 8px 14px; font-size: 12px; font-weight: 600;
  background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.2);
  border-radius: 8px; color: #f87171; cursor: pointer; transition: all 0.2s ease; white-space: nowrap;
}
.btn-add-small:hover { background: rgba(239,68,68,0.2); }
.btn-add-small.green { background: rgba(52,211,153,0.12); border-color: rgba(52,211,153,0.2); color: #34d399; }
.btn-add-small.green:hover { background: rgba(52,211,153,0.2); }
.list-items { display: flex; flex-direction: column; gap: 6px; }
.list-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px; background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04); border-radius: 10px;
  transition: all 0.15s ease;
}
.list-item:hover { background: rgba(255,255,255,0.04); }
.item-black { border-left: 3px solid rgba(248,113,113,0.3); }
.item-white { border-left: 3px solid rgba(52,211,153,0.3); }
.item-info { flex: 1; min-width: 0; }
.item-url { font-size: 12px; color: rgba(255,255,255,0.65); font-family: monospace; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-reason { font-size: 11px; color: rgba(255,255,255,0.25); margin-top: 2px; }
.btn-remove {
  width: 26px; height: 26px; display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; color: rgba(255,255,255,0.3); font-size: 16px; cursor: pointer;
  transition: all 0.15s ease; flex-shrink: 0;
}
.btn-remove:hover { background: rgba(239,68,68,0.15); color: #f87171; border-color: rgba(239,68,68,0.2); }
.list-empty { text-align: center; padding: 30px; color: rgba(255,255,255,0.15); font-size: 13px; }
.section-title { font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.7); margin-bottom: 20px; }
.freq-config { max-width: 500px; }
.freq-row { margin-bottom: 20px; }
.freq-label { display: block; font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.4); margin-bottom: 8px; }
.slider-group { display: flex; align-items: center; gap: 14px; }
.slider { flex: 1; accent-color: #4c6ef5; }
.slider-val { font-size: 14px; font-weight: 700; color: #7c8aff; min-width: 40px; text-align: right; }
.btn-save-freq {
  padding: 10px 24px; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease; margin-top: 8px;
  box-shadow: 0 2px 12px rgba(76, 110, 245, 0.3);
}
.btn-save-freq:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(76, 110, 245, 0.45); }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  padding: 12px 16px; text-align: left; font-weight: 600;
  color: rgba(255,255,255,0.35); font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid rgba(255,255,255,0.06);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table td {
  padding: 12px 16px; color: rgba(255,255,255,0.6);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.data-table tbody tr:hover { background: rgba(76,110,245,0.04); }
.task-name { font-weight: 500; color: rgba(255,255,255,0.75); }
.btn-sm {
  padding: 4px 12px; font-size: 11px; font-weight: 500;
  background: rgba(76,110,245,0.1); border: 1px solid rgba(76,110,245,0.15);
  border-radius: 6px; color: #7c8aff; cursor: pointer; transition: all 0.2s ease;
}
.btn-sm:hover { background: rgba(76,110,245,0.2); }
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal-card {
  background: rgba(22,27,34,0.96);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px; padding: 32px; min-width: 400px;
  box-shadow: 0 16px 64px rgba(0,0,0,0.5);
}
.modal-title { font-size: 18px; font-weight: 700; color: rgba(255,255,255,0.85); margin-bottom: 24px; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.35); margin-bottom: 6px; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
.btn-cancel {
  padding: 10px 22px; font-size: 13px; font-weight: 500;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; color: rgba(255,255,255,0.45); cursor: pointer; transition: all 0.2s ease;
}
.btn-cancel:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7); }
.btn-confirm {
  padding: 10px 22px; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  border: none; border-radius: 10px; color: #fff; cursor: pointer; transition: all 0.25s ease;
  box-shadow: 0 2px 12px rgba(76, 110, 245, 0.3);
}
.btn-confirm:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(76, 110, 245, 0.45); }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .two-col { grid-template-columns: 1fr; }
  .modal-card { min-width: auto; width: 90%; padding: 24px; }
}
@media (max-width: 560px) {
  .add-row { flex-direction: column; }
}
</style>