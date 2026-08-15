# PyPad

**PyPad — AI-Powered Python Learning OS**

AI 驱动的 Python 学习操作系统

## 项目结构

```
PyPad/
├── pypad-frontend/    # 前端项目 (Vue 3 + Vite)
├── pypad-backend/     # 后端项目 (Python FastAPI)
├── docs/              # 项目文档
│   └── competition/   # 参赛材料
├── tests/             # 测试文件
└── docker-compose.yml # Docker 编排配置
```

## 快速开始

### 前端开发

```bash
cd pypad-frontend
npm install
npm run dev
```

### 后端开发

```bash
cd pypad-backend
pip install -r requirements.txt
python main.py
```

### Docker 部署

```bash
docker-compose up
```

## 技术栈

- **前端**: Vue 3, TypeScript, Vite, Tailwind CSS, Monaco Editor
- **后端**: Python, FastAPI, SQLModel, MySQL
- **AI**: OpenAI / Ollama / Mock 模式

## 产品定位

PyPad 是一个 AI 驱动的 Python 学习操作系统，提供：

- 智能知识图谱
- AI 代码审查
- 个性化学习路径
- 实时代码执行环境
