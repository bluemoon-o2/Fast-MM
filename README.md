<h1 align="center">🤖 Fast-MM</h1>
<p align="center">
    <img src="./docs/icon.png" height="250px">
</p>
<h4 align="center">
    融合工程化架构与深度数学逻辑的下一代数学建模 Agent<br>
    Next-Gen Mathematical Modeling Agent with Deep Logic
</h4>

<h5 align="center">简体中文 | <a href="README_EN.md">English</a></h5>

<p align="center">
    <a href="https://github.com/bluemoon-o2/Fast-MM" target="_blank">
        <img src="https://img.shields.io/github/stars/bluemoon-o2/Fast-MM?style=for-the-badge&color=brightgreen&logo=github" alt="GitHub Stars">
    </a>
    <a href="https://github.com/bluemoon-o2/Fast-MM/blob/main/LICENSE" target="_blank">
        <img src="https://img.shields.io/github/license/bluemoon-o2/Fast-MM?style=for-the-badge&color=orange" alt="License">
    </a>
    <a href="https://docker.com/" target="_blank">
        <img src="https://img.shields.io/badge/Docker-Supported-blue?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Supported">
    </a>
    <a href="https://python.org/" target="_blank">
        <img src="https://img.shields.io/badge/Python-3.10+-purple?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
    </a>
    <a href="https://vuejs.org/" target="_blank">
        <img src="https://img.shields.io/badge/Vue-3-green?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue 3">
    </a>
    <a href="https://fastapi.tiangolo.com/" target="_blank">
        <img src="https://img.shields.io/badge/FastAPI-Async-yellow?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI Async">
    </a>
    <a href="https://github.com/bluemoon-o2/Fast-MM/pulls" target="_blank">
        <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
    </a>
</p>

## 🌟 项目简介 (Project Overview)

**Fast-MM** 是一个专为数学建模竞赛设计的端到端自动化辅助系统。它旨在解决数学建模竞赛中时间紧迫、任务繁重的痛点，通过自动化处理从问题分析、数学公式推导、编程求解到学术论文写作的全流程，帮助参赛队伍高效产出高质量的竞赛作品。

### ♨️ 核心进化 (Key Evolutions)

- **🚀 从线性到 DAG**: 摒弃简单的线性执行流程，引入 **DAG (有向无环图)** 进行复杂任务的依赖分析与并行编排。
- **🔄 Actor-Critic 迭代**: 在建模 (Modeler) 和编程 (Coder) 环节引入“生成-评价-修正”闭环，显著提升模型准确性与代码一次运行成功率。
- **🛡️ 自愈式代码执行**: 代码生成模块具备 **Self-Healing** 能力，能够根据报错信息自动 Debug 并重试（最大重试次数可配置）。
- **📄 结构化中间表达**: 采用标准化的数据结构在 Agent 之间传递信息，确保逻辑严密性。

## ✨ 核心功能 (Features)

### 🤖 多智能体协作体系 (Multi-Agent Architecture)

| 智能体 (Agent) | 主要职能 | 关键能力 |
| :--- | :--- | :--- |
| **Coordinator Agent** | 任务编排 | 问题拆解、DAG 构建、依赖分析 |
| **Modeler Agent** | 数学建模 | 问题分析、方法检索 (HMML)、Actor-Critic 迭代修正、公式推导 |
| **Coder Agent** | 代码执行 | 多环境支持 (Jupyter/E2B/Daytona)、自愈式 Debug (Max 5 Retries)、Traceback 分析 |
| **Writer Agent** | 论文生成 | 结果整合、学术搜索 (OpenAlex)、基于模板的写作 |

### 🚀 系统核心能力

- **DAG 任务编排**: 利用大模型分析任务间的输入输出依赖，构建有向无环图，支持复杂逻辑流转。
- **自愈式代码执行**: 自动捕获运行时错误（Traceback），分析原因并重新生成代码，支持最大 5 次自动重试。
- **灵活的 LLM 配置**: 支持为每个 Agent 独立配置不同的 LLM 模型（如 OpenAI, DeepSeek, Ollama 等），优化成本与性能。
- **方法库集成**: 内置 **HMML (Hierarchical Mathematical Modeling Methods Library)**，支持自动检索最匹配的数学方法。
- **多环境支持**: 代码执行层解耦，支持本地 Jupyter Kernel 或云端安全沙盒 (E2B, Daytona)。
- **实时进度反馈**: 基于 WebSocket 的全双工通信，实时推送任务状态、中间结果和日志信息。

## 🛠️ 技术栈 (Technology Stack)

Fast-MM 基于现代化的技术栈构建，确保高性能与可扩展性：

- **前端层 (Frontend)**:
    - **Vue 3**: 响应式 UI 组件构建
    - **TailwindCSS**: 现代化的原子类样式设计
    - **WebSocket Client**: 实时双向通信处理

- **后端层 (Backend)**:
    - **FastAPI**: 高性能异步 HTTP/WebSocket 框架
    - **Python 3.10+**: 核心运行环境
    - **Uvicorn**: 生产级 ASGI 服务器

- **基础设施 (Infrastructure)**:
    - **Redis**: 任务队列管理 & Pub/Sub 消息总线
    - **LiteLLM**: 统一的 LLM 接口抽象层
    - **Jupyter Kernel**: 本地 Python 代码执行环境
    - **(Optional) E2B / Daytona**: 云端安全代码沙盒

- **数据与知识 (Data & Knowledge)**:
    - **HMML.json**: 分层数学建模方法库
    - **Markdown Templates**: 标准化论文结构模板
    - **OpenAlex API**: 学术文献检索服务

## 🏗️ 系统架构与流程 (Architecture & Flow)

### 系统处理流程

1. **任务提交 (POST /api/v1/task)**: 用户上传题目与数据，后端创建 Task 并推入 Redis 队列。
2. **编排 (Coordinator)**: `CoordinatorAgent` 分析题目，构建任务 DAG，确定子任务执行顺序。
3. **建模 (Modeler)**: `ModelerAgent` 根据子任务检索 HMML，生成数学模型，并通过 Actor-Critic 循环进行自我修正。
4. **求解 (Coder)**: `CoderAgent` 接收模型定义，在沙盒环境中生成并执行代码。如遇报错，触发 Self-Healing 机制自动修复。
5. **写作 (Writer)**: `WriterAgent` 整合所有中间结果（公式、代码、图表），调用 OpenAlex 搜索相关文献，基于模板生成最终论文。

<p align="left">
    <img src="https://img.shields.io/badge/TailwindCSS-3.0+-teal?style=flat&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
    <img src="https://img.shields.io/badge/Redis-Task%20Queue-red?style=flat&logo=redis&logoColor=white" alt="Redis">
    <img src="https://img.shields.io/badge/Jupyter-Kernel-orange?style=flat&logo=jupyter&logoColor=white" alt="Jupyter Kernel">
    <img src="https://img.shields.io/badge/WebSocket-Real%20Time-pink?style=flat&logo=websocket&logoColor=white" alt="WebSocket">
</p>

- **Frontend**: Vue 3 + TailwindCSS + WebSocket
- **Backend**: FastAPI (Async) + Redis (Task Queue)
- **Core Logic**: Multi-Agent System with DAG Orchestration & Actor-Critic Loop

## 🚀 快速开始 (Quick Start)

### 🐳 方案一：Docker 部署（推荐）

最简单的方式，无需配置复杂的本地环境。

```bash
docker-compose up
```

### 🛠️ 方案二：本地开发

适合开发者进行二次开发调试。

**1. 后端启动**
```bash
cd backend
# 使用 uv 安装依赖 (推荐)
uv sync
# 启动服务
uvicorn app.main:app --reload
```

**2. 前端启动**
```bash
cd frontend
pnpm install
pnpm dev
```

## 📜 版权与致谢 (Copyright & Acknowledgements)

本项目基于开源社区的优秀成果进行开发，特此声明并致谢：

- **[MathModelAgent](https://github.com/jihe520/MathModelAgent)**: 
    - 提供了本项目的基础 Web 工程架构、前后端交互协议及基础 Agent 框架。
    - 版权所有 © [jihe520](https://github.com/jihe520) 及贡献者。

- **[MM-Agent](https://github.com/Turing-Project/MM-Agent)** (参考):
    - 为本项目提供了核心的数学建模深度逻辑、DAG 任务编排思想及 Actor-Critic 迭代算法参考。
    - 感谢 MM-Agent 团队在自动化数学建模领域的探索与贡献。