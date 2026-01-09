<h1 align="center">🤖 Fast-MM</h1>
<p align="center">
    <img src="./docs/icon.png" height="250px">
</p>
<h4 align="center">
    Next-Gen Mathematical Modeling Agent with Deep Logic<br>
    Integrating Engineering Architecture with Advanced Math Reasoning
</h4>

<h5 align="center"><a href="README.md">简体中文</a> | English</h5>

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

## 🌟 Project Overview

**Fast-MM** is an automated assistance system designed specifically for mathematical modeling competitions. It automates the entire process from problem analysis and model construction to code solution and paper writing, helping teams efficiently produce high-quality competition submissions.

It adopts modern engineering architecture (FastAPI + Vue3 + Redis + WebSocket) and deep mathematical logic (DAG task orchestration, Actor-Critic iteration mechanism), aiming to provide users with an intelligent modeling assistant that possesses both high-performance solving capabilities and an exceptional user experience.

### Key Evolutions

- **🚀 From Linear to DAG**: Moving away from simple linear execution, we introduce **DAG (Directed Acyclic Graph)** for complex task dependency analysis and parallel orchestration.
- **🔄 Actor-Critic Iteration**: Implementing a "Generate-Evaluate-Refine" loop in both modeling (Modeler) and coding (Coder) phases, significantly improving model accuracy and one-shot code success rates.
- **🛡️ Self-Healing Code Execution**: The code generation module features **Self-Healing** capabilities, automatically debugging and retrying based on error messages.
- **📄 Structured Intermediate Representation**: Using standardized data structures to pass information between agents, ensuring logical rigor throughout the process.

## ✨ Core Features

- **🧠 Intelligent Task Orchestration (Coordinator Agent)**
    - Deeply understands competition problems and automatically decomposes sub-tasks.
    - Constructs DAG dependency graphs to scientifically plan solution paths.
- **📐 Iterative Modeling (Modeler Agent)**
    - Introduces a Critic role for model auditing.
    - Supports formula derivation and self-correction, outputting high-quality LaTeX/Markdown model descriptions.
- **💻 Robust Code Execution (Coder Agent)**
    - **Multi-Environment Support**: Local Jupyter Kernel or Cloud Sandboxes (E2B/Daytona).
    - **Auto-Correction**: Automatically analyzes Tracebacks and fixes code upon runtime errors (Max Retries: 5).
- **📝 Automated Paper Writing (Writer Agent)**
    - Real-time integration of modeling results and charts.
    - Generates complete papers following academic standards.
- **🖥️ Modern Interaction Experience**
    - Real-time WebSocket progress updates.
    - Visualized task execution flow.

## 🏗️ Architecture

<p align="left">
    <img src="https://img.shields.io/badge/TailwindCSS-3.0+-teal?style=flat&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
    <img src="https://img.shields.io/badge/Redis-Task%20Queue-red?style=flat&logo=redis&logoColor=white" alt="Redis">
    <img src="https://img.shields.io/badge/Jupyter-Kernel-orange?style=flat&logo=jupyter&logoColor=white" alt="Jupyter Kernel">
    <img src="https://img.shields.io/badge/WebSocket-Real%20Time-pink?style=flat&logo=websocket&logoColor=white" alt="WebSocket">
</p>

- **Frontend**: Vue 3 + TailwindCSS + WebSocket
- **Backend**: FastAPI (Async) + Redis (Task Queue)
- **Core Logic**: Multi-Agent System with DAG Orchestration & Actor-Critic Loop

## 🚀 Quick Start

### 🐳 Option 1: Docker Deployment (Recommended)

The simplest way, no complex local environment setup required.

```bash
docker-compose up
```

### 🛠️ Option 2: Local Development

Suitable for developers for secondary development and debugging.

**1. Backend Startup**
```bash
cd backend
# Install dependencies using uv (recommended)
uv sync
# Start the service
uvicorn app.main:app --reload
```

**2. Frontend Startup**
```bash
cd frontend
pnpm install
pnpm dev
```

## 📜 Copyright & Acknowledgements

This project is developed based on excellent achievements from the open-source community:

- **[MathModelAgent](https://github.com/jihe520/MathModelAgent)**: 
    - Provided the base Web engineering architecture, frontend-backend interaction protocols, and basic agent framework.
    - Copyright © [jihe520](https://github.com/jihe520) and contributors.

- **[MM-Agent](https://github.com/Turing-Project/MM-Agent)** (Reference):
    - Provided core mathematical modeling logic, DAG task orchestration concepts, and Actor-Critic iteration algorithm references.
    - Special thanks to the MM-Agent team for their exploration and contributions in automated mathematical modeling.
