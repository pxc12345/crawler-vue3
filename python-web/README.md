# CrawlMaster 爬虫管理系统 - 前端

基于 **Vue 3 + Vite + Element Plus** 的爬虫任务管理前端，与 `python` 目录下的 Flask 后端配合使用。

## 技术栈

- Vue 3、Vue Router、Pinia
- Vite 4
- Element Plus
- Axios

## 项目结构

```
python-web/
├── .env                 # API 地址配置（本地 / 远程切换，见下文）
├── .env.example         # 配置模板
├── src/
│   ├── api/             # 接口封装
│   ├── components/      # 公共组件
│   ├── config/api.js    # API 基址解析
│   ├── views/           # 页面（任务、数据、监控等）
│   └── router/          # 路由
├── vite.config.js       # 开发服务器与代理
├── start.bat            # Windows 启动脚本
└── start.sh             # Mac/Linux 启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
cd python-web
npm install
```

### 2. 配置 API 地址

编辑 **`python-web/.env`**（仅此一个文件，注释切换即可）：

```env
# 远程 Render 后端（默认）
VITE_API_BASE_URL=https://crawler-vue3.onrender.com/api

# 本地 Flask 后端（联调时启用）
# VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

| 场景 | 操作 |
|------|------|
| 使用**远程**后端 | 保留远程行有效，本地行注释 |
| 使用**本地**后端 | 注释远程行，取消本地行注释 |
| 修改后生效 | **重启** `npm run dev`，浏览器硬刷新 |

> **注意**：不要创建 `.env.local`，Vite 会优先读取它并覆盖 `.env` 中的配置。

**如何判断当前连的是哪套后端？**  
打开浏览器 F12 → Network，查看接口完整 URL：

- `https://crawler-vue3.onrender.com/api/...` → 远程
- `http://127.0.0.1:5000/api/...` → 本地直连
- `http://localhost:3000/api/...` → 本地代理（未配置 `VITE_API_BASE_URL` 时）

### 3. 启动本地后端（仅本地联调需要）

```bash
cd ../python
python app.py
```

默认地址：`http://127.0.0.1:5000`

### 4. 启动前端

```bash
npm run dev
```

访问：**http://localhost:3000**

Windows 也可双击 `start.bat`。

## 主要功能

- 任务管理：创建、启动、重新启动、停止、编辑、删除
- 任务模板：保存与复用采集配置
- 数据预览、清洗、导出
- 代理池、反爬、告警、系统监控与日志
- 多主题、使用说明（导航栏「使用说明」）

## 任务操作说明

| 按钮 | 说明 |
|------|------|
| **启动** | 新任务直接运行；已运行过的任务会复制为新任务记录再启动 |
| **重新启动** | 在当前任务上再次执行，不新建任务记录 |
| **停止** | 停止运行中的任务 |

## 构建与部署

```bash
npm run build
```

构建产物在 `dist/`。部署到 Render 等平台时，可在平台环境变量中设置 `VITE_API_BASE_URL` 覆盖 `.env`。

## 常见问题

1. **改了 `.env` 仍连本地**  
   检查是否存在 `.env.local` 并删除；确认已重启 dev 服务。

2. **跨域错误**  
   远程后端需在 `python/.env` 的 `CORS_ORIGINS` 中放行前端域名。

3. **时间显示偏差 8 小时**  
   确保后端为最新代码并已重启；前端会自动发送 `X-Timezone` 请求头。

## 相关文档

- 系统内使用说明：登录后访问 **使用说明** 页面
- 后端环境变量：见 `python/.env.example`
