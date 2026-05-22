<template>
  <div class="templates-page">
    <NavBar />
    <div class="templates-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">任务模板</h1>
          <span class="template-count">{{ templates.length }} 个模板</span>
        </div>
        <button class="btn-create" @click="showCreateModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          创建模板
        </button>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 4" :key="n" class="skeleton-card">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-80"></div>
        </div>
      </div>

      <div v-else-if="templates.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
        </div>
        <p class="empty-text">暂无任务模板</p>
        <p class="empty-desc">创建一个模板来快速启动常用配置的任务</p>
      </div>

      <div v-else class="template-grid">
        <div v-for="tmpl in templates" :key="tmpl.id" class="template-card">
          <div class="template-card-top">
            <div class="template-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <div class="template-info">
              <h3 class="template-name">{{ tmpl.name }}</h3>
              <p class="template-desc">{{ tmpl.description }}</p>
            </div>
          </div>

          <div class="template-meta">
            <div class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
              </svg>
              <span>使用 {{ tmpl.useCount }} 次</span>
            </div>
            <div class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>{{ tmpl.createdAt }}</span>
            </div>
          </div>

          <div class="template-actions">
            <button class="action-btn primary" @click="useTemplate(tmpl)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              使用模板
            </button>
            <button class="action-btn" @click="editTemplate(tmpl)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              编辑
            </button>
            <button class="action-btn danger" @click="deleteTemplate(tmpl)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h2 class="modal-title">{{ editingTemplate ? '编辑模板' : '创建模板' }}</h2>
            <button class="modal-close" @click="closeModal">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">模板名称</label>
              <input v-model="modalForm.name" type="text" class="form-input" placeholder="例如：电商商品采集模板" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea v-model="modalForm.description" class="form-textarea" rows="2" placeholder="简要描述此模板的用途..."></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Cron 表达式</label>
              <input v-model="modalForm.cron" type="text" class="form-input" placeholder="0 */6 * * *" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">并发数</label>
                <input v-model.number="modalForm.concurrency" type="number" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">请求间隔 (ms)</label>
                <input v-model.number="modalForm.interval" type="number" class="form-input" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="closeModal">取消</button>
            <button class="modal-btn primary" @click="saveTemplate">
              {{ editingTemplate ? '保存修改' : '创建模板' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const loading = ref(true)
const templates = ref([])
const showCreateModal = ref(false)
const editingTemplate = ref(null)

const modalForm = reactive({
  name: '',
  description: '',
  cron: '',
  concurrency: 5,
  interval: 2000
})

function useTemplate(tmpl) {
  router.push({
    path: '/tasks/new',
    query: {
      templateId: tmpl.id,
      name: tmpl.name,
      cron: tmpl.cron,
      concurrency: tmpl.concurrency,
      interval: tmpl.interval
    }
  })
}

function editTemplate(tmpl) {
  editingTemplate.value = tmpl
  modalForm.name = tmpl.name
  modalForm.description = tmpl.description
  modalForm.cron = tmpl.cron
  modalForm.concurrency = tmpl.concurrency
  modalForm.interval = tmpl.interval
  showCreateModal.value = true
}

function deleteTemplate(tmpl) {
  const confirmed = window.confirm(`确定要删除模板「${tmpl.name}」吗？`)
  if (confirmed) {
    templates.value = templates.value.filter(t => t.id !== tmpl.id)
  }
}

function saveTemplate() {
  if (!modalForm.name.trim()) return

  if (editingTemplate.value) {
    const idx = templates.value.findIndex(t => t.id === editingTemplate.value.id)
    if (idx !== -1) {
      templates.value[idx] = {
        ...templates.value[idx],
        name: modalForm.name,
        description: modalForm.description,
        cron: modalForm.cron,
        concurrency: modalForm.concurrency,
        interval: modalForm.interval
      }
    }
  } else {
    const newId = Math.max(...templates.value.map(t => t.id), 0) + 1
    templates.value.push({
      id: newId,
      name: modalForm.name,
      description: modalForm.description,
      cron: modalForm.cron,
      concurrency: modalForm.concurrency,
      interval: modalForm.interval,
      useCount: 0,
      createdAt: new Date().toLocaleDateString('zh-CN')
    })
  }
  closeModal()
}

function closeModal() {
  showCreateModal.value = false
  editingTemplate.value = null
  modalForm.name = ''
  modalForm.description = ''
  modalForm.cron = ''
  modalForm.concurrency = 5
  modalForm.interval = 2000
}

async function fetchTemplates() {
  loading.value = true
  await new Promise(r => setTimeout(r, 400))
  templates.value = [
    { id: 1, name: '电商商品采集', description: '适用于主流电商平台的商品信息采集，支持分页和详情页爬取', cron: '0 */6 * * *', concurrency: 5, interval: 2000, useCount: 128, createdAt: '2026-03-15' },
    { id: 2, name: '新闻资讯爬取', description: '定时采集新闻网站的最新资讯内容，支持多源聚合', cron: '0 */2 * * *', concurrency: 3, interval: 1000, useCount: 67, createdAt: '2026-02-20' },
    { id: 3, name: '社交媒体监控', description: '监控社交媒体平台的关键词和话题趋势', cron: '*/30 * * * *', concurrency: 8, interval: 500, useCount: 204, createdAt: '2026-01-10' },
    { id: 4, name: '金融行情采集', description: '实时采集股票、汇率等金融数据，支持多市场数据源', cron: '*/5 * * * *', concurrency: 10, interval: 200, useCount: 89, createdAt: '2025-12-01' },
    { id: 5, name: '房源信息采集', description: '采集各大房产平台的房源信息，含价格走势和区域分析', cron: '0 */12 * * *', concurrency: 4, interval: 3000, useCount: 42, createdAt: '2025-10-18' },
    { id: 6, name: '招聘信息汇总', description: '从多个招聘网站收集职位信息，支持按行业和地区筛选', cron: '0 */8 * * *', concurrency: 6, interval: 1500, useCount: 156, createdAt: '2025-09-05' }
  ]
  loading.value = false
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.templates-page {
  min-height: 100vh;
  background-color: #0d1117;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}

.templates-page::before {
  content: '';
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16, 185, 129, 0.04), transparent);
  pointer-events: none; z-index: 0;
}

.templates-content {
  max-width: 1080px; margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 28px;
}

.header-left {
  display: flex; align-items: baseline; gap: 14px;
}

.page-title {
  font-size: 26px; font-weight: 700;
  color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;
}

.template-count {
  font-size: 13px; color: rgba(255, 255, 255, 0.35); font-weight: 500;
}

.btn-create {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 22px;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  color: #fff; border: none; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(76, 110, 245, 0.3);
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(76, 110, 245, 0.45);
}

.btn-create svg { width: 18px; height: 18px; }

.skeleton-list { display: flex; flex-direction: column; gap: 12px; }
.skeleton-card {
  background: rgba(22, 27, 34, 0.5); border-radius: 16px;
  padding: 28px; border: 1px solid rgba(255, 255, 255, 0.04);
}
.skeleton-line {
  height: 14px; background: rgba(255, 255, 255, 0.04);
  border-radius: 7px; margin-bottom: 10px;
  animation: shimmer 1.5s ease-in-out infinite;
}
.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }
.skeleton-line.w-80 { width: 80%; }
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

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.template-card {
  background: rgba(22, 27, 34, 0.55);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px; padding: 24px;
  transition: all 0.3s ease;
}

.template-card:hover {
  background: rgba(22, 27, 34, 0.8);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.template-card-top {
  display: flex; align-items: flex-start; gap: 14px;
  margin-bottom: 16px;
}

.template-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: rgba(76, 110, 245, 0.12);
  color: #7c8aff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.template-icon svg { width: 22px; height: 22px; }

.template-info { flex: 1; min-width: 0; }

.template-name {
  font-size: 15px; font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px; letter-spacing: -0.2px;
}

.template-desc {
  font-size: 12px; color: rgba(255, 255, 255, 0.35);
  line-height: 1.4;
}

.template-meta {
  display: flex; gap: 20px; margin-bottom: 16px;
}

.meta-item {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: rgba(255, 255, 255, 0.3);
}

.meta-item svg {
  width: 14px; height: 14px;
  color: rgba(255, 255, 255, 0.15);
}

.template-actions {
  display: flex; gap: 8px;
  padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.action-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 7px 14px; font-size: 12px; font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px; color: rgba(255, 255, 255, 0.5);
  cursor: pointer; transition: all 0.2s ease;
}

.action-btn svg { width: 14px; height: 14px; }

.action-btn:hover { color: rgba(255, 255, 255, 0.85); background: rgba(255, 255, 255, 0.08); }

.action-btn.primary {
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  color: #fff; border: none;
  box-shadow: 0 2px 10px rgba(76, 110, 245, 0.25);
}

.action-btn.primary:hover {
  box-shadow: 0 4px 16px rgba(76, 110, 245, 0.4);
  transform: translateY(-1px);
}

.action-btn.danger:hover {
  color: #f87171; border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.1);
}

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: rgba(22, 27, 34, 0.96);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px; width: 520px; max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalIn 0.3s cubic-bezier(0.22, 0.61, 0.36, 1);
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 22px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-title {
  font-size: 18px; font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.modal-close {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  background: transparent; border: none;
  color: rgba(255, 255, 255, 0.4); font-size: 22px;
  cursor: pointer; border-radius: 8px; transition: all 0.2s ease;
}

.modal-close:hover { color: rgba(255, 255, 255, 0.8); background: rgba(255, 255, 255, 0.05); }

.modal-body { padding: 24px; display: flex; flex-direction: column; gap: 16px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }

.form-label {
  font-size: 12px; font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase; letter-spacing: 0.5px;
}

.form-input {
  width: 100%; padding: 11px 16px; font-size: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px; color: rgba(255, 255, 255, 0.85);
  outline: none; transition: all 0.25s ease;
}

.form-input:focus {
  border-color: rgba(76, 110, 245, 0.4);
  box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.08);
}

.form-textarea {
  width: 100%; padding: 11px 16px; font-size: 13px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px; color: rgba(255, 255, 255, 0.85);
  outline: none; resize: vertical; transition: all 0.25s ease;
}

.form-textarea:focus { border-color: rgba(76, 110, 245, 0.4); }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 20px 24px; border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-btn {
  padding: 10px 22px; font-size: 13px; font-weight: 600;
  border-radius: 10px; cursor: pointer; transition: all 0.25s ease;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.5);
}

.modal-btn:hover { background: rgba(255, 255, 255, 0.08); color: rgba(255, 255, 255, 0.75); }

.modal-btn.primary {
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  color: #fff; border: none;
  box-shadow: 0 4px 14px rgba(76, 110, 245, 0.3);
}

.modal-btn.primary:hover { box-shadow: 0 6px 20px rgba(76, 110, 245, 0.45); }

@media (max-width: 768px) {
  .template-grid { grid-template-columns: 1fr; }
  .templates-content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .form-row { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  .template-actions { flex-wrap: wrap; }
}
</style>