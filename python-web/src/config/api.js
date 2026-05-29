/**
 * API 基址：在 python-web/.env 中配置 VITE_API_BASE_URL（远程/本地二选一，注释切换）
 * 未配置时 dev 模式走 Vite 代理 /api → localhost:5000
 */
function trimTrailingSlash(url) {
  return url.replace(/\/+$/, '')
}

const configured = import.meta.env.VITE_API_BASE_URL
  ? trimTrailingSlash(import.meta.env.VITE_API_BASE_URL)
  : ''

/** axios 使用的 baseURL（含 /api 前缀） */
export const API_BASE_URL = configured || '/api'

/** 无 /api 后缀的服务根地址（student 等直连 /students 路由） */
export const API_ORIGIN = configured
  ? configured.replace(/\/api$/, '')
  : import.meta.env.DEV
    ? 'http://localhost:5000'
    : ''
