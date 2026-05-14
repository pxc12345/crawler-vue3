<template>
  <div class="app-container">
    <header class="app-header">
      <h1>🎓 学生管理系统</h1>
      <p>基于 Vue 3 + Python Flask 的前后端分离应用</p>
    </header>

    <div v-if="error" class="error" @click="error = ''">
      ❌ {{ error }}
    </div>

    <div class="toolbar">
      <div class="search-box">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="🔍 搜索学生姓名..."
          @input="handleSearch"
        />
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        ➕ 添加学生
      </button>
      <button class="btn btn-warning" @click="loadStudents">
        🔄 刷新
      </button>
    </div>

    <Statistics :statistics="statistics" />

    <div v-if="loading" class="loading">
      ⏳ 加载中...
    </div>

    <div v-else-if="students.length === 0" class="empty">
      <h3>📭 暂无学生数据</h3>
      <p>点击"添加学生"按钮创建第一条记录</p>
    </div>

    <table v-else class="student-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>姓名</th>
          <th>年龄</th>
          <th>成绩</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in students" :key="student.student_id">
          <td>{{ student.student_id }}</td>
          <td>{{ student.name }}</td>
          <td>{{ student.age }}</td>
          <td>
            <span :class="getGradeClass(student.grade)">
              {{ student.grade }}
            </span>
          </td>
          <td class="actions">
            <button class="btn btn-primary btn-sm" @click="openEditModal(student)">
              ✏️ 编辑
            </button>
            <button class="btn btn-danger btn-sm" @click="handleDelete(student.student_id)">
              🗑️ 删除
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

function getGradeClass(grade) {
  if (grade >= 90) return 'grade-excellent'
  if (grade >= 80) return 'grade-good'
  if (grade >= 60) return 'grade-pass'
  return 'grade-fail'
}

onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.grade-excellent {
  color: #2ecc71;
  font-weight: bold;
}

.grade-good {
  color: #3498db;
  font-weight: bold;
}

.grade-pass {
  color: #f39c12;
}

.grade-fail {
  color: #e74c3c;
}
</style>
