<template>
  <div class="app-container">
    <header class="app-header">
      <h1>学生管理系统</h1>
      <p>基于 Vue 3 + Python Flask 的前后端分离应用</p>
    </header>

    <div v-if="error" class="error-toast" @click="error = ''">
      {{ error }}
    </div>

    <div class="toolbar">
      <div class="search-box">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索学生姓名..."
          @input="handleSearch"
        />
      </div>
      <div class="toolbar-actions">
        <button class="btn btn-secondary" @click="openAddModal">
          添加学生
        </button>
        <button class="btn btn-secondary" @click="handleExport">
          导出
        </button>
        <button class="btn btn-secondary" @click="triggerImport">
          导入
        </button>
        <input
          ref="importInput"
          type="file"
          accept=".csv"
          style="display: none"
          @change="handleImport"
        />
      </div>
    </div>

    <Statistics :statistics="statistics" />

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="students.length === 0" class="empty">
      <h3>暂无学生数据</h3>
      <p>点击"添加学生"按钮创建第一条记录</p>
    </div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>头像</th>
          <th>ID</th>
          <th>姓名</th>
          <th>年龄</th>
          <th>成绩</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in students" :key="student.student_id">
          <td class="avatar-cell">
            <div class="avatar" :class="{ 'has-avatar': student.avatar_url }">
              <img v-if="student.avatar_url" :src="getFullAvatarUrl(student.avatar_url)" alt="avatar" />
              <span v-else>{{ student.name.charAt(0) }}</span>
            </div>
          </td>
          <td>{{ student.student_id }}</td>
          <td>{{ student.name }}</td>
          <td>{{ student.age }}</td>
          <td>
            <span :class="getGradeClass(student.grade)">
              {{ student.grade }}
            </span>
          </td>
          <td class="actions">
            <button class="btn btn-text" @click="openEditModal(student)">
              编辑
            </button>
            <button class="btn btn-text btn-danger" @click="handleDelete(student.student_id)">
              删除
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <StudentForm
      v-if="showModal"
      :student="selectedStudent"
      @close="closeModal"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { studentApi } from './api/student.js'
import Statistics from './components/Statistics.vue'
import StudentForm from './components/StudentForm.vue'

const students = ref([])
const statistics = ref({})
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const showModal = ref(false)
const selectedStudent = ref(null)
const importInput = ref(null)

async function loadStudents() {
  loading.value = true
  error.value = ''
  try {
    const res = await studentApi.getAll()
    students.value = res.data
    await loadStatistics()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadStatistics() {
  try {
    const res = await studentApi.getStatistics()
    statistics.value = res.data
  } catch (e) {
    console.error('获取统计失败:', e)
  }
}

async function handleSearch() {
  if (!searchKeyword.value.trim()) {
    await loadStudents()
    return
  }
  loading.value = true
  try {
    const res = await studentApi.search(searchKeyword.value)
    students.value = res.data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  selectedStudent.value = null
  showModal.value = true
}

function openEditModal(student) {
  selectedStudent.value = { ...student }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedStudent.value = null
}

async function handleSubmit(studentData) {
  try {
    if (selectedStudent.value) {
      await studentApi.update(selectedStudent.value.student_id, studentData)
    } else {
      await studentApi.create(studentData)
    }
    closeModal()
    await loadStudents()
  } catch (e) {
    error.value = e.message
    throw e
  }
}

async function handleDelete(id) {
  if (!confirm('确定要删除这个学生吗？')) return
  try {
    await studentApi.delete(id)
    await loadStudents()
  } catch (e) {
    error.value = e.message
  }
}

function handleExport() {
  studentApi.exportStudents()
}

function triggerImport() {
  importInput.value.click()
}

async function handleImport(event) {
  const file = event.target.files[0]
  if (!file) return

  try {
    const res = await studentApi.importStudents(file)
    if (res.code === 200) {
      alert(res.message)
      await loadStudents()
    } else {
      alert(res.message)
    }
  } catch (e) {
    alert('导入失败: ' + e.message)
  }

  event.target.value = ''
}

function getGradeClass(grade) {
  if (grade >= 90) return 'grade-a'
  if (grade >= 80) return 'grade-b'
  if (grade >= 60) return 'grade-c'
  return 'grade-d'
}

function getFullAvatarUrl(url) {
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:5000${url}`
}

onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.grade-a {
  color: #2d8cf0;
  font-weight: 600;
}

.grade-b {
  color: #19be6b;
  font-weight: 600;
}

.grade-c {
  color: #ff9900;
}

.grade-d {
  color: #ed4014;
}
</style>