<template>
  <div class="templates-page">
    <NavBar />
    <div class="templates-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">任务模板</h1>
          <span class="template-count">{{ templates.length }} 个模板</span>
        </div>
        <button class="btn-create" @click="openCreateModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          创建模板
        </button>
      </div>

      <div class="filter-bar">
        <div class="category-filter">
          <button
            v-for="cat in categoryOptions"
            :key="cat.value"
            class="cat-btn"
            :class="{ active: activeCategory === cat.value }"
            @click="setCategory(cat.value)"
          >{{ cat.label }}</button>
        </div>
        <label class="fav-only-label">
          <input type="checkbox" v-model="favoriteOnly" @change="fetchTemplates" />
          <span>仅常用</span>
        </label>
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
        <div v-for="tmpl in templates" :key="tmpl.id" class="template-card" :class="{ 'is-favorite': tmpl.isFavorite }">
          <div class="template-card-top">
            <div class="template-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <div class="template-info">
              <div class="name-row">
                <h3 class="template-name">{{ tmpl.name }}</h3>
                <button
                  type="button"
                  class="btn-fav"
                  :class="{ active: tmpl.isFavorite }"
                  :title="tmpl.isFavorite ? '取消常用' : '设为常用'"
                  @click.stop="toggleFavorite(tmpl)"
                >
                  <svg viewBox="0 0 24 24" :fill="tmpl.isFavorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.5">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </button>
              </div>
              <p class="template-desc">{{ tmpl.description || '暂无描述' }}</p>
              <span class="category-tag">{{ tmpl.categoryLabel }}</span>
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
            <button class="action-btn primary" :disabled="actionLoading" @click="useTemplate(tmpl)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              使用模板
            </button>
            <button class="action-btn" @click="previewTemplate(tmpl)">预览</button>
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

    <!-- 创建/编辑 -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card modal-card-lg">
          <div class="modal-header">
            <h2 class="modal-title">{{ editingTemplate ? '编辑模板' : '创建模板' }}</h2>
            <button class="modal-close" @click="closeModal">&times;</button>
          </div>
          <div class="modal-body modal-body-scroll">
            <div class="form-group">
              <label class="form-label">模板名称</label>
              <input v-model="modalForm.name" type="text" class="form-input" placeholder="例如：电商商品采集模板" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea v-model="modalForm.description" class="form-textarea" rows="2" placeholder="简要描述此模板的用途..."></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">分类</label>
                <select v-model="modalForm.category" class="form-input">
                  <option v-for="c in categorySelectOptions" :key="c.value" :value="c.value">{{ c.label }}</option>
                </select>
              </div>
              <div class="form-group fav-check-group">
                <label class="form-label">常用模板</label>
                <label class="inline-check">
                  <input type="checkbox" v-model="modalForm.isFavorite" />
                  <span>设为常用</span>
                </label>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">目标 URL</label>
              <input v-model="modalForm.targetUrl" type="text" class="form-input" placeholder="https://example.com" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">执行周期（分钟）</label>
                <input v-model.number="modalForm.intervalMinutes" type="number" class="form-input" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">爬取页数</label>
                <input v-model.number="modalForm.totalPages" type="number" class="form-input" min="1" max="100" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">并发数</label>
                <input v-model.number="modalForm.concurrency" type="number" class="form-input" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">请求间隔 (秒)</label>
                <input v-model.number="modalForm.intervalSeconds" type="number" class="form-input" min="1" max="60" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">最大重试次数</label>
                <input v-model.number="modalForm.maxRetries" type="number" class="form-input" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">重试间隔 (秒)</label>
                <input v-model.number="modalForm.retryInterval" type="number" class="form-input" min="1" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">爬取模式</label>
                <select v-model="modalForm.crawlMode" class="form-input">
                  <option value="link">链接模式</option>
                  <option value="image">图片模式</option>
                  <option value="mixed">混合模式</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">任务类型</label>
                <select v-model="modalForm.taskType" class="form-input">
                  <option value="crawler">爬虫任务</option>
                  <option value="data_collection">数据采集</option>
                  <option value="monitor">监控任务</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">代理组</label>
              <input v-model="modalForm.proxyGroup" type="text" class="form-input" placeholder="留空则不使用代理组" />
            </div>
            <div class="form-group">
              <label class="form-label">请求头 (JSON)</label>
              <textarea v-model="modalForm.headers" class="form-textarea" rows="3" placeholder='{"User-Agent": "..."}'></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="closeModal">取消</button>
            <button class="modal-btn primary" :disabled="saving" @click="saveTemplate">
              {{ saving ? '保存中...' : (editingTemplate ? '保存修改' : '创建模板') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 预览 -->
    <Teleport to="body">
      <div v-if="showPreviewModal" class="modal-overlay" @click.self="showPreviewModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h2 class="modal-title">模板预览 · {{ previewItem?.name }}</h2>
            <button class="modal-close" @click="showPreviewModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <p v-if="previewItem?.description" class="preview-desc">{{ previewItem.description }}</p>
            <dl class="preview-list">
              <div v-for="line in previewLines" :key="line.label" class="preview-row">
                <dt>{{ line.label }}</dt>
                <dd>{{ line.value }}</dd>
              </div>
            </dl>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="showPreviewModal = false">关闭</button>
            <button class="modal-btn primary" @click="useTemplate(previewItem); showPreviewModal = false">使用此模板</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TEMPLATE_CATEGORIES,
  categoryLabel,
  buildTemplateConfig,
  applyTemplateToModalForm,
  getTemplatePreviewLines,
  getDefaultModalForm,
  parseTemplateConfig
} from '../utils/templateConfig'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const actionLoading = ref(false)
const templates = ref([])
const showCreateModal = ref(false)
const showPreviewModal = ref(false)
const editingTemplate = ref(null)
const previewItem = ref(null)
const activeCategory = ref('all')
const favoriteOnly = ref(false)

const categoryOptions = TEMPLATE_CATEGORIES
const categorySelectOptions = TEMPLATE_CATEGORIES.filter(c => c.value !== 'all')

const modalForm = reactive(getDefaultModalForm())

const previewLines = computed(() => {
  if (!previewItem.value) return []
  return getTemplatePreviewLines(previewItem.value.config)
})

function openCreateModal() {
  editingTemplate.value = null
  Object.assign(modalForm, getDefaultModalForm())
  showCreateModal.value = true
}

function setCategory(value) {
  activeCategory.value = value
  fetchTemplates()
}

function mapTemplateFromApi(item) {
  const config = parseTemplateConfig(item.config)
  return {
    id: item.id,
    name: item.name,
    description: item.description || '',
    category: item.category || 'general',
    categoryLabel: categoryLabel(item.category || 'general'),
    isFavorite: item.is_favorite === 1 || item.is_favorite === true,
    config,
    useCount: item.use_count || 0,
    createdAt: item.created_at || ''
  }
}

async function useTemplate(tmpl) {
  if (!tmpl?.id) return
  actionLoading.value = true
  try {
    const res = await taskAPI.useTemplate(tmpl.id)
    if (res.data.success) {
      const data = res.data.data
      ElMessage.success('已加载模板配置，正在前往新建任务')
      router.push({
        path: '/tasks/new',
        query: { templateId: String(tmpl.id) }
      })
      if (data) {
        const idx = templates.value.findIndex(t => t.id === tmpl.id)
        if (idx >= 0) {
          templates.value[idx] = mapTemplateFromApi(data)
        }
      }
    } else {
      ElMessage.error(res.data.message || '应用模板失败')
    }
  } catch (e) {
    ElMessage.error('应用模板失败')
  } finally {
    actionLoading.value = false
  }
}

function previewTemplate(tmpl) {
  previewItem.value = tmpl
  showPreviewModal.value = true
}

function editTemplate(tmpl) {
  editingTemplate.value = tmpl
  modalForm.name = tmpl.name
  modalForm.description = tmpl.description
  modalForm.category = tmpl.category || 'general'
  modalForm.isFavorite = tmpl.isFavorite
  applyTemplateToModalForm(modalForm, tmpl.config)
  showCreateModal.value = true
}

async function toggleFavorite(tmpl) {
  try {
    const res = await taskAPI.toggleTemplateFavorite(tmpl.id)
    if (res.data.success) {
      tmpl.isFavorite = res.data.data?.is_favorite ?? !tmpl.isFavorite
      ElMessage.success(res.data.message)
      if (favoriteOnly.value && !tmpl.isFavorite) {
        templates.value = templates.value.filter(t => t.id !== tmpl.id)
      }
    } else {
      ElMessage.error(res.data.message || '操作失败')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function deleteTemplate(tmpl) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板「${tmpl.name}」吗？`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await taskAPI.deleteTemplate(tmpl.id)
    if (res.data.success) {
      templates.value = templates.value.filter(t => t.id !== tmpl.id)
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(res.data.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error('删除失败')
    }
  }
}

async function saveTemplate() {
  if (!modalForm.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }

  saving.value = true
  try {
    const payload = {
      name: modalForm.name.trim(),
      description: modalForm.description.trim(),
      category: modalForm.category,
      is_favorite: modalForm.isFavorite,
      config: buildTemplateConfig(modalForm)
    }

    let res
    if (editingTemplate.value) {
      res = await taskAPI.updateTemplate(editingTemplate.value.id, payload)
    } else {
      res = await taskAPI.createTemplate(payload)
    }

    if (res.data.success) {
      ElMessage.success(editingTemplate.value ? '模板已更新' : '创建模板成功')
      closeModal()
      fetchTemplates()
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function closeModal() {
  showCreateModal.value = false
  editingTemplate.value = null
  Object.assign(modalForm, getDefaultModalForm())
}

async function fetchTemplates() {
  loading.value = true
  try {
    const params = {}
    if (activeCategory.value !== 'all') {
      params.category = activeCategory.value
    }
    if (favoriteOnly.value) {
      params.favorite_only = '1'
    }
    const res = await taskAPI.getTemplates(params)
    if (res.data.success) {
      templates.value = (res.data.data || []).map(mapTemplateFromApi)
    } else {
      ElMessage.error(res.data.message || '获取模板列表失败')
    }
  } catch (e) {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.templates-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
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
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 12px;
  flex-wrap: wrap;
}

.category-filter {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}

.cat-btn {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-btn.active {
  color: var(--active-color);
  background: var(--active-bg);
  font-weight: 600;
}

.fav-only-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
}

.fav-only-label input { accent-color: var(--accent-primary); }

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
  background: var(--gradient-primary);
  color: #fff; border: none; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(var(--accent-rgb), 0.3);
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(76, 110, 245, 0.45);
}

.btn-create svg { width: 18px; height: 18px; }

.skeleton-list { display: flex; flex-direction: column; gap: 12px; }
.skeleton-card {
  background: var(--bg-card); border-radius: 16px;
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
.empty-text { font-size: 18px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; }
.empty-desc { font-size: 13px; color: var(--text-muted); }

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.template-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px; padding: 24px;
  transition: all 0.3s ease;
}

.template-card.is-favorite {
  border-color: rgba(251, 191, 36, 0.25);
}

.template-card:hover {
  background: var(--bg-card);
  border-color: var(--border-color);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.template-card-top {
  display: flex; align-items: flex-start; gap: 14px;
  margin-bottom: 16px;
}

.template-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: rgba(var(--accent-rgb), 0.12);
  color: var(--active-color);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.template-icon svg { width: 22px; height: 22px; }

.template-info { flex: 1; min-width: 0; }

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-fav {
  padding: 2px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.25);
  cursor: pointer;
  flex-shrink: 0;
}

.btn-fav svg { width: 16px; height: 16px; }
.btn-fav.active { color: #fbbf24; }

.template-name {
  font-size: 15px; font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px; letter-spacing: -0.2px;
  flex: 1;
  min-width: 0;
}

.template-desc {
  font-size: 12px; color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 6px;
}

.category-tag {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(var(--accent-rgb), 0.12);
  color: var(--active-color);
}

.template-meta {
  display: flex; gap: 20px; margin-bottom: 16px;
}

.meta-item {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-muted);
}

.meta-item svg {
  width: 14px; height: 14px;
  color: rgba(255, 255, 255, 0.15);
}

.template-actions {
  display: flex; gap: 8px; flex-wrap: wrap;
  padding-top: 14px; border-top: 1px solid var(--border-color);
}

.action-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 7px 14px; font-size: 12px; font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.2s ease;
}

.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.action-btn svg { width: 14px; height: 14px; }

.action-btn:hover:not(:disabled) { color: var(--text-primary); background: rgba(255, 255, 255, 0.08); }

.action-btn.primary {
  background: var(--gradient-primary);
  color: #fff; border: none;
  box-shadow: 0 2px 10px rgba(var(--accent-rgb), 0.25);
}

.action-btn.primary:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(var(--accent-rgb), 0.4);
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
  background: var(--bg-card);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  border-radius: 18px; width: 520px; max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalIn 0.3s cubic-bezier(0.22, 0.61, 0.36, 1);
}

.modal-card-lg { width: 640px; max-height: 90vh; display: flex; flex-direction: column; }

.modal-body-scroll {
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 22px 24px; border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
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

.modal-body { padding: 24px; display: flex; flex-direction: column; gap: 16px; }

.preview-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.preview-list { margin: 0; }

.preview-row {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}

.preview-row:last-child { border-bottom: none; }

.preview-row dt { color: var(--text-muted); font-weight: 600; }
.preview-row dd { color: var(--text-primary); margin: 0; word-break: break-all; }

.form-group { display: flex; flex-direction: column; gap: 6px; }

.fav-check-group { justify-content: flex-end; }

.inline-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  padding-top: 8px;
}

.form-label {
  font-size: 12px; font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.5px;
}

.form-input {
  width: 100%; padding: 11px 16px; font-size: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px; color: var(--text-primary);
  outline: none; transition: all 0.25s ease;
}

.form-input:focus {
  border-color: rgba(76, 110, 245, 0.4);
  box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.08);
}

select.form-input {
  color-scheme: dark;
  cursor: pointer;
}

select.form-input option {
  background-color: #161b22;
  color: rgba(255, 255, 255, 0.92);
}

.form-textarea {
  width: 100%; padding: 11px 16px; font-size: 13px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-primary);
  outline: none; resize: vertical; transition: all 0.25s ease;
  font-family: inherit;
}

.form-textarea:focus { border-color: rgba(var(--accent-rgb), 0.4); }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 20px 24px; border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.modal-btn {
  padding: 10px 22px; font-size: 13px; font-weight: 600;
  border-radius: 10px; cursor: pointer; transition: all 0.25s ease;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary);
}

.modal-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.modal-btn:hover:not(:disabled) { background: rgba(255, 255, 255, 0.08); color: var(--text-primary); }

.modal-btn.primary {
  background: var(--gradient-primary);
  color: #fff; border: none;
  box-shadow: 0 4px 14px rgba(var(--accent-rgb), 0.3);
}

.modal-btn.primary:hover:not(:disabled) { box-shadow: 0 6px 20px rgba(var(--accent-rgb), 0.45); }

@media (max-width: 768px) {
  .template-grid { grid-template-columns: 1fr; }
  .templates-content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .form-row { grid-template-columns: 1fr; }
  .modal-card-lg { width: 95vw; }
}

@media (max-width: 480px) {
  .template-actions { flex-wrap: wrap; }
}
</style>
