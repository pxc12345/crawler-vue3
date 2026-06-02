import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Show from '@/views/Show.vue'
import Admin from '@/views/Admin.vue'
import AdminUser from '@/views/AdminUser.vue'
import AdminTheme from '@/views/AdminTheme.vue'
import AdminContent from '@/views/AdminContent.vue'
import AdminEffect from '@/views/AdminEffect.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: Login },
    { path: '/show', name: 'Show', component: Show },
    { path: '/admin', name: 'Admin', component: Admin },
    { path: '/admin/user', name: 'AdminUser', component: AdminUser },
    { path: '/admin/theme', name: 'AdminTheme', component: AdminTheme },
    { path: '/admin/content', name: 'AdminContent', component: AdminContent },
    { path: '/admin/effect', name: 'AdminEffect', component: AdminEffect },
  ],
})

router.beforeEach((to, _from, next) => {
  const role = sessionStorage.getItem('blessing_role')
  if (to.path.startsWith('/admin')) {
    if (role !== 'admin') {
      next('/login')
      return
    }
  }
  if (to.path === '/show') {
    if (!role) {
      next('/login')
      return
    }
  }
  next()
})

export default router
