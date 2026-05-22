import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue')
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPassword.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/crawler',
    name: 'Crawler',
    component: () => import('../views/Crawler.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/new',
    name: 'TaskNew',
    component: () => import('../views/TaskNew.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: () => import('../views/TaskDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/:id/versions',
    name: 'TaskVersions',
    component: () => import('../views/TaskVersions.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/task-templates',
    name: 'TaskTemplates',
    component: () => import('../views/TaskTemplates.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/Alerts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/data-preview',
    name: 'DataPreview',
    component: () => import('../views/DataPreview.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/data-clean',
    name: 'DataClean',
    component: () => import('../views/DataClean.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/data-export',
    name: 'DataExport',
    component: () => import('../views/DataExport.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/proxy-pool',
    name: 'ProxyPool',
    component: () => import('../views/ProxyPool.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/anti-crawl',
    name: 'AntiCrawl',
    component: () => import('../views/AntiCrawl.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/system-monitor',
    name: 'SystemMonitor',
    component: () => import('../views/SystemMonitor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/system-logs',
    name: 'SystemLogs',
    component: () => import('../views/SystemLogs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workspace',
    name: 'Workspace',
    component: () => import('../views/Workspace.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  const isLoggedIn = authStore.isAuthenticated || 
                     (localStorage.getItem('access_token') && localStorage.getItem('user'))
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
