<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBlessingStore } from '@/stores/blessing'
import { deleteTheme, getThemeList, saveTheme } from '@/utils/api'

const router = useRouter()
const store = useBlessingStore()

const categories = ['高级粉色系', '高级紫色系', '高级蓝色系', '多色系混搭主题']
const themes = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  name: '',
  category: categories[0],
  background_color: '#fff1ee',
  title_color: '#8a2d3b',
  body_color: '#473334',
  button_color: '#cf6f5d',
  card_color: '#fffaf7',
  sort: 0,
})

const groupedThemes = computed(() =>
  categories.map((category) => ({
    category,
    items: themes.value.filter((item) => item.category === category),
  })),
)

onMounted(async () => {
  store.restoreUser()
  if (store.role !== 'admin') {
    router.push('/login')
    return
  }
  await loadThemes()
})

async function loadThemes() {
  loading.value = true
  try {
    const res: any = await getThemeList()
    if (res.code === 200) {
      themes.value = res.data || []
    }
  } catch {
    showToast('加载主题失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  form.value = {
    name: '',
    category: categories[0],
    background_color: '#fff1ee',
    title_color: '#8a2d3b',
    body_color: '#473334',
    button_color: '#cf6f5d',
    card_color: '#fffaf7',
    sort: 0,
  }
}

function editTheme(theme: any) {
  editingId.value = theme.id
  form.value = {
    name: theme.name,
    category: theme.category,
    background_color: theme.background_color,
    title_color: theme.title_color,
    body_color: theme.body_color,
    button_color: theme.button_color,
    card_color: theme.card_color,
    sort: theme.sort || 0,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function handleSave() {
  if (!form.value.name.trim()) {
    showToast('请输入主题名称')
    return
  }
  saving.value = true
  try {
    const res: any = await saveTheme({ ...form.value, id: editingId.value || undefined })
    if (res.code === 200) {
      showToast(editingId.value ? '主题已更新' : '主题已创建')
      resetForm()
      await loadThemes()
    } else {
      showToast(res.msg || '保存失败')
    }
  } catch {
    showToast('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function handleDelete(theme: any) {
  if (!confirm(`确定删除主题「${theme.name}」吗？`)) return
  try {
    const res: any = await deleteTheme(theme.id)
    if (res.code === 200) {
      showToast('主题已删除')
      await loadThemes()
      if (editingId.value === theme.id) resetForm()
    } else {
      showToast(res.msg || '删除失败')
    }
  } catch {
    showToast('删除失败，请重试')
  }
}

function showToast(msg: string) {
  const el = document.createElement('div')
  el.className = 'toast'
  el.textContent = msg
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 2200)
}
</script>

<template>
  <div class="theme-page">
    <header class="theme-header">
      <button class="btn-secondary" @click="router.push('/admin')">返回</button>
      <div class="header-copy">
        <p class="header-eyebrow">Theme System</p>
        <h1>主题模板管理</h1>
      </div>
      <button class="btn-small" @click="resetForm">新建</button>
    </header>

    <main class="theme-content">
      <section class="editor-panel">
        <div class="editor-copy">
          <p class="panel-kicker">更多色系，更大反差</p>
          <h2>{{ editingId ? '编辑主题' : '创建主题' }}</h2>
          <p>每套主题都要拉开层次：背景、标题、正文、按钮、卡片底色不再挤成一团，预览区会实时显示整体气质。</p>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>主题名称</span>
            <input v-model="form.name" class="input-field glass-input" maxlength="60" placeholder="例如：绯绒玫瑰" />
          </label>

          <label class="field">
            <span>主题分类</span>
            <select v-model="form.category" class="input-field glass-input">
              <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
            </select>
          </label>

          <label class="field">
            <span>背景色</span>
            <input v-model="form.background_color" type="color" class="color-field" />
          </label>

          <label class="field">
            <span>标题色</span>
            <input v-model="form.title_color" type="color" class="color-field" />
          </label>

          <label class="field">
            <span>正文色</span>
            <input v-model="form.body_color" type="color" class="color-field" />
          </label>

          <label class="field">
            <span>按钮色</span>
            <input v-model="form.button_color" type="color" class="color-field" />
          </label>

          <label class="field">
            <span>卡片底色</span>
            <input v-model="form.card_color" type="color" class="color-field" />
          </label>
        </div>

        <div class="live-preview" :style="{ backgroundColor: form.background_color, color: form.body_color }">
          <div class="preview-card" :style="{ backgroundColor: form.card_color }">
            <p class="preview-kicker">{{ form.category }}</p>
            <h3 :style="{ color: form.title_color }">{{ form.name || '主题预览' }}</h3>
            <p>这是一套完整主题的展示效果。让背景柔和、标题醒目、正文耐读、按钮有存在感，卡片底色负责把内容托起来。</p>
            <button :style="{ backgroundColor: form.button_color }">进入祝福</button>
          </div>
        </div>

        <button class="btn-primary save-btn" :disabled="saving" @click="handleSave">
          {{ saving ? '保存中' : '保存主题' }}
        </button>
      </section>

      <section class="theme-library">
        <div class="library-head">
          <div>
            <p class="panel-kicker">Theme Library</p>
            <h2>现有成品主题</h2>
          </div>
          <p class="library-tip">每个色系都扩成了更有区别的版本，避免看起来像同一个颜色换深浅。</p>
        </div>

        <div v-if="loading" class="loading">加载中...</div>

        <section v-for="group in groupedThemes" :key="group.category" class="group">
          <h3>{{ group.category }}</h3>
          <div class="theme-grid">
            <article v-for="theme in group.items" :key="theme.id" class="theme-card" :style="{ backgroundColor: theme.background_color }">
              <div class="theme-card-inner" :style="{ backgroundColor: theme.card_color, color: theme.body_color }">
                <p class="card-category">{{ theme.category }}</p>
                <h4 :style="{ color: theme.title_color }">{{ theme.name }}</h4>
                <div class="swatches">
                  <span v-for="color in [theme.background_color, theme.title_color, theme.body_color, theme.button_color, theme.card_color]" :key="color" :style="{ backgroundColor: color }"></span>
                </div>
                <button class="mini-demo" :style="{ backgroundColor: theme.button_color }">下一步</button>
                <div class="card-actions">
                  <button class="btn-small" @click="editTheme(theme)">编辑</button>
                  <button class="btn-danger" @click="handleDelete(theme)">删除</button>
                </div>
              </div>
            </article>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<style scoped>
.theme-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(212, 111, 93, 0.14), transparent 28%),
    radial-gradient(circle at right center, rgba(59, 130, 246, 0.14), transparent 25%),
    linear-gradient(180deg, #f8f3eb 0%, #efe5d9 100%);
}

.theme-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 18px;
  background: rgba(255, 250, 244, 0.9);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(124, 97, 70, 0.12);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-eyebrow,
.panel-kicker,
.preview-kicker,
.card-category {
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.header-eyebrow,
.panel-kicker,
.preview-kicker,
.card-category {
  color: #9f7857;
}

.header-copy h1,
.editor-copy h2,
.library-head h2,
.group h3 {
  color: #2f2721;
  font-weight: 900;
}

.header-copy h1 {
  font-size: 1.12rem;
}

.theme-content {
  padding: 18px;
  display: grid;
  gap: 16px;
}

.editor-panel,
.theme-library,
.theme-card-inner {
  border-radius: 22px;
  border: 1px solid rgba(121, 94, 68, 0.12);
  background: rgba(255, 251, 246, 0.88);
  box-shadow: 0 18px 40px rgba(77, 58, 39, 0.08);
}

.editor-panel,
.theme-library {
  padding: 20px;
}

.editor-copy p,
.library-tip {
  color: #665447;
  line-height: 1.7;
}

.editor-copy h2,
.library-head h2 {
  font-size: 1.28rem;
  margin: 4px 0 8px;
}

.form-grid {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.field span {
  display: block;
  color: #7b6352;
  font-size: 0.79rem;
  font-weight: 800;
  margin-bottom: 7px;
}

.glass-input {
  background: rgba(255, 255, 255, 0.84);
  border-color: rgba(177, 146, 118, 0.22);
}

.color-field {
  width: 100%;
  height: 52px;
  border: 1px solid rgba(177, 146, 118, 0.22);
  border-radius: 16px;
  background: #fff;
  padding: 6px;
}

.live-preview {
  margin-top: 18px;
  border-radius: 24px;
  padding: 14px;
}

.preview-card {
  border-radius: 20px;
  padding: 22px;
  box-shadow: 0 16px 36px rgba(41, 28, 22, 0.1);
}

.preview-card h3 {
  font-size: 1.34rem;
  margin: 6px 0 10px;
}

.preview-card p {
  line-height: 1.75;
}

.preview-card button,
.mini-demo {
  color: #fff;
  border: 0;
  border-radius: 14px;
  padding: 10px 16px;
  margin-top: 14px;
  font-weight: 800;
}

.save-btn {
  width: 100%;
  margin-top: 16px;
}

.library-head {
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
}

.group + .group {
  margin-top: 18px;
}

.theme-grid {
  display: grid;
  gap: 12px;
}

.theme-card {
  border-radius: 22px;
  padding: 12px;
}

.theme-card-inner {
  padding: 18px;
}

.theme-card h4 {
  font-size: 1.14rem;
  font-weight: 900;
  margin-top: 4px;
}

.swatches {
  display: flex;
  gap: 8px;
  margin: 14px 0 8px;
}

.swatches span {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 14px;
}

.loading {
  text-align: center;
  color: #8c735f;
  padding: 18px;
}
</style>
