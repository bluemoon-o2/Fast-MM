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

**Fast-MM** 是一个专为数学建模竞赛设计的自动化辅助系统。它能够自动完成从问题分析、模型构建、代码求解到论文写作的全流程，帮助参赛队伍高效产出高质量的竞赛作品。

### 核心进化 (Key Evolutions)

- **🚀 从线性到 DAG**: 摒弃简单的线性执行流程，引入 **DAG (有向无环图)** 进行复杂任务的依赖分析与并行编排。
- **🔄 Actor-Critic 迭代**: 在建模 (Modeler) 和编程 (Coder) 环节引入“生成-评价-修正”闭环，显著提升模型准确性与代码一次运行成功率。
- **🛡️ 自愈式代码执行**: 代码生成模块具备 **Self-Healing** 能力，能够根据报错信息自动 Debug 并重试。
- **📄 结构化中间表达**: 采用标准化的数据结构在 Agent 之间传递信息，确保逻辑严密性。

## ✨ 核心功能 (Features)

- **🧠 智能任务编排 (Coordinator Agent)**
    - 深度理解赛题，自动拆解子任务。
    - 构建 DAG 依赖图，科学规划解题路径。
- **📐 深度迭代建模 (Modeler Agent)**
    - 引入 Critic 角色进行模型审核。
    - 支持公式推导与自我修正，输出高质量 Latex/Markdown 模型描述。
- **💻 鲁棒代码执行 (Coder Agent)**
    - **多环境支持**: 本地 Jupyter Kernel 或云端沙盒 (E2B/Daytona)。
    - **自动纠错**: 遇到运行时错误自动分析 Traceback 并修正代码 (Max Retries: 5)。
- **📝 自动化论文撰写 (Writer Agent)**
    - 实时整合建模结果与图表。
    - 生成符合学术规范的完整论文。
- **🖥️ 现代化交互体验**
    - 实时 WebSocket 进度推送。
    - 可视化任务执行流。

## 🏗️ 技术架构 (Architecture)

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