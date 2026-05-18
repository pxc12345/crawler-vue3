# 用户登录系统 - 完整实现

基于Python Flask + Vue3的完整用户认证系统，包含登录、注册、忘记密码等功能。

## 技术栈

### 后端
- Python 3.x
- Flask (Web框架)
- Flask-CORS (跨域处理)
- PyJWT (JWT Token)
- bcrypt (密码加密)
- PyMySQL (数据库)

### 前端
- Vue 3 (Composition API)
- Vue Router 4 (路由管理)
- Pinia (状态管理)
- Axios (HTTP客户端)
- Vite (构建工具)

## 功能特性

### 后端功能
✅ 用户注册（用户名、邮箱、手机号）
✅ 用户登录（支持用户名/邮箱登录）
✅ JWT Token认证（Access Token + Refresh Token）
✅ Token自动刷新
✅ Token黑名单
✅ 密码加密存储（bcrypt）
✅ 登录失败次数限制 + 账户锁定
✅ 密码重置流程
✅ 验证码发送与验证
✅ 安全审计日志
✅ 密码历史记录（防止重复使用）
✅ 统一API响应格式

### 前端功能
✅ 响应式登录页面
✅ 表单实时验证
✅ 密码强度检测
✅ 密码显示/隐藏
✅ 按钮加载状态
✅ 注册页面
✅ 忘记密码流程（多步）
✅ 重置密码页面
✅ 个人中心（修改密码）
✅ 登录状态保持
✅ 自动Token刷新
✅ 路由守卫

## 项目结构

```
c:\test\
├── python\                      # 后端服务
│   ├── src\
│   │   ├── notifications\       # 通知模块
│   │   │   ├── verification_service.py
│   │   │   ├── email_sender.py
│   │   │   └── sms_sender.py
│   │   ├── auth_service.py      # 认证服务
│   │   └── notification_db.py   # 数据库操作
│   ├── auth_server.py           # Flask应用入口
│   ├── requirements.txt         # Python依赖
│   └── ...
│
└── python-web\                  # 前端服务
    ├── src\
    │   ├── api\                 # API客户端
    │   │   └── index.js
    │   ├── stores\              # Pinia状态管理
    │   │   └── auth.js
    │   ├── router\              # Vue Router
    │   │   └── index.js
    │   ├── views\               # 页面组件
    │   │   ├── Login.vue
    │   │   ├── Register.vue
    │   │   ├── ForgotPassword.vue
    │   │   ├── ResetPassword.vue
    │   │   ├── Home.vue
    │   │   └── Profile.vue
    │   ├── App.vue
    │   ├── main.js
    │   └── style.css
    ├── package.json
    ├── vite.config.js
    └── ...
```

## 快速开始

### 1. 安装后端依赖

```bash
cd python
pip install -r requirements.txt
```

### 2. 配置数据库

确保MySQL服务正在运行，并在 `src/notification_db.py` 中配置数据库连接信息：
- host: localhost
- port: 3308
- user: root
- password: Pxc7890.
- database: school_db

### 3. 启动后端服务

```bash
cd python
python auth_server.py
```

后端服务将在 http://localhost:5000 启动

### 4. 安装前端依赖

```bash
cd python-web
npm install
```

### 5. 启动前端服务

```bash
cd python-web
npm run dev
```

前端服务将在 http://localhost:5173 启动

## API接口文档

### 认证接口

| 接口 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/auth/register` | POST | 用户注册 | 否 |
| `/api/auth/login` | POST | 用户登录 | 否 |
| `/api/auth/refresh` | POST | 刷新Token | 否 |
| `/api/auth/logout` | POST | 用户登出 | 是 |
| `/api/auth/forgot-password/send-code` | POST | 发送重置验证码 | 否 |
| `/api/auth/forgot-password/verify-code` | POST | 验证重置验证码 | 否 |
| `/api/auth/forgot-password/reset` | POST | 重置密码 | 否 |
| `/api/auth/change-password` | POST | 修改密码 | 是 |

### 用户接口

| 接口 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/user/profile` | GET | 获取用户信息 | 是 |

### 统一响应格式

```json
{
  "success": true/false,
  "message": "描述信息",
  "code": "错误码",
  "data": {}
}
```

## 数据库表结构

### users（用户表）
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- phone: 手机号（唯一）
- password_hash: 密码哈希
- login_attempts: 登录失败次数
- locked_until: 账户锁定时间
- last_login_at: 最后登录时间
- created_at: 创建时间
- updated_at: 更新时间

### verification_codes（验证码表）
- id: 主键
- user_id: 用户ID
- code: 验证码
- code_type: 验证码类型（email/sms）
- target: 发送目标
- expires_at: 过期时间
- used: 是否已使用
- created_at: 创建时间

### token_blacklist（Token黑名单）
- id: 主键
- token: Token内容
- expires_at: 过期时间
- created_at: 创建时间

### password_history（密码历史）
- id: 主键
- user_id: 用户ID
- password_hash: 历史密码哈希
- created_at: 创建时间

### audit_logs（审计日志）
- id: 主键
- user_id: 用户ID
- action: 操作类型
- ip_address: IP地址
- user_agent: User Agent
- details: 详细信息
- created_at: 创建时间

## 安全特性

1. **密码安全**
   - bcrypt加密存储
   - 密码强度检测
   - 历史密码检查

2. **登录安全**
   - 登录失败次数限制（默认5次）
   - 账户自动锁定（默认15分钟）
   - 审计日志记录

3. **Token安全**
   - JWT签名认证
   - Access Token短期有效（30分钟）
   - Refresh Token长期有效（7天）
   - Token黑名单机制

4. **CORS配置**
   - 白名单域名控制
   - 允许的HTTP方法
   - 允许的请求头

## 使用说明

### 注册账号
1. 访问注册页面
2. 填写用户名（必填）、邮箱（可选）、手机号（可选）
3. 设置密码（至少6位）
4. 提交注册

### 登录系统
1. 使用用户名或邮箱登录
2. 输入密码
3. 登录成功后跳转到首页

### 忘记密码
1. 点击"忘记密码"
2. 输入注册邮箱或手机号
3. 接收并输入验证码
4. 设置新密码
5. 使用新密码登录

### 修改密码
1. 登录后进入个人中心
2. 输入原密码
3. 输入新密码（不能与最近使用的密码相同）
4. 确认修改

## 开发说明

### 后端扩展
- 修改 `auth_service.py` 中的配置可调整安全策略
- 在 `notification_db.py` 中添加新的数据库操作
- 在 `auth_server.py` 中添加新的API端点

### 前端扩展
- 在 `views/` 目录中添加新页面
- 在 `router/index.js` 中配置路由
- 在 `stores/auth.js` 中管理认证状态
- 在 `api/index.js` 中添加API调用

## 注意事项

1. 生产环境请修改JWT密钥（`auth_service.py` 中的 `SECRET_KEY`）
2. 生产环境请禁用debug模式
3. 建议使用HTTPS协议
4. 数据库密码等敏感信息建议使用环境变量
5. 验证码发送功能需要配置实际的邮件或短信服务

## 许可证

MIT License
