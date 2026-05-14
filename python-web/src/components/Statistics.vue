<template>
  <div class="statistics">
    <div class="stat-card">
      <h3>{{ statistics.total || 0 }}</h3>
      <p>学生总数</p>
    </div>
    <div class="stat-card">
      <h3>{{ formatNumber(statistics.average_age) }}</h3>
      <p>平均年龄</p>
    </div>
    <div class="stat-card">
      <h3>{{ formatNumber(statistics.average_grade) }}</h3>
      <p>平均成绩</p>
    </div>
    <div class="stat-card">
      <h3>{{ statistics.highest_grade ?? '-' }}</h3>
      <p>最高成绩</p>
    </div>
    <div class="stat-card">
      <h3>{{ statistics.lowest_grade ?? '-' }}</h3>
      <p>最低成绩</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  statistics: {
    type: Object,
    default: () => ({})
  }
})

function formatNumber(num) {
  if (num === undefined || num === null) return '-'
  return Number(num).toFixed(1)
}
</script>