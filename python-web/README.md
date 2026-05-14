# 学生管理系统 - Vue3 前端

基于 Vue 3 + Vite 构建的学生管理系统前端。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **Fetch API** - 与后端通信

## 项目结构

```
python-web/
├── src/
│   ├── api/
│   │   └── student.js      # API调用模块
│   ├── components/
│   │   ├── Statistics.vue   # 统计组件
│   │   └── StudentForm.vue  # 表单组件
│   ├── App.vue             # 主组件
│   ├── main.js             # 入口文件
│   └── style.css           # 全局样式
├── index.html               # HTML入口
├── package.json             # 项目配置
├── vite.config.js          # Vite配置
├── start.bat               # Windows启动脚本
└── start.sh                # Mac/Linux启动脚本
```

## 快速开始

### 1. 安装 Node.js

下载并安装: https://nodejs.org/

### 2. 启动后端

```bash
cd ../python
python app.py
```

后端地址: http://127.0.0.1:5000

### 3. 启动前端

**Windows:**
```bash
双击 start.bat
```

**或手动启动:**
```bash
npm install
npm run dev
```

前端地址: http://localhost:3000

## 功能列表

- ✅ 查看所有学生
- ✅ 搜索学生
- ✅ 添加学生
- ✅ 编辑学生
- ✅ 删除学生
- ✅ 查看统计信息（总数、平均年龄、平均成绩等）
- ✅ 实时刷新

## 注意事项

1. 确保 **Python 后端** 已启动在 5000 端口
2. 前端默认连接: http://127.0.0.1:5000
3. 如果端口被占用，修改 `vite.config.js` 中的 port
