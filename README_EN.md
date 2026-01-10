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

**Fast-MM** is an end-to-end automated assistance system designed specifically for mathematical modeling competitions. It addresses the time-intensive and labor-intensive nature of competitions by automating the complete workflow from problem analysis, mathematical derivation, and coding solution to academic paper writing, helping teams efficiently produce high-quality submissions.

### ♨️ Key Evolutions

- **🚀 From Linear to DAG**: Moving away from simple linear execution, we introduce **DAG (Directed Acyclic Graph)** for complex task dependency analysis and parallel orchestration.
- **🔄 Actor-Critic Iteration**: Implementing a "Generate-Evaluate-Refine" loop in both modeling (Modeler) and coding (Coder) phases, significantly improving model accuracy and one-shot code success rates.
- **🛡️ Self-Healing Code Execution**: The code generation module features **Self-Healing** capabilities, automatically debugging and retrying based on error messages (configurable max retries).
- **📄 Structured Intermediate Representation**: Using standardized data structures to pass information between agents, ensuring logical rigor throughout the process.

## ✨ Core Features

### 🤖 Multi-Agent Architecture

| Agent | Primary Function | Key Capabilities |
| :--- | :--- | :--- |
| **Coordinator Agent** | Task Orchestration | Problem decomposition, DAG construction, dependency analysis |
| **Modeler Agent** | Math Modeling | Problem analysis, method retrieval (HMML), Actor-Critic refinement, formula derivation |
| **Coder Agent** | Code Execution | Multi-environment support (Jupyter/E2B/Daytona), Self-Healing Debug (Max 5 Retries), Traceback analysis |
| **Writer Agent** | Paper Generation | Result integration, scholarly search (OpenAlex), template-based writing |

### 🚀 System Capabilities

- **DAG Task Orchestration**: Uses LLMs to analyze input/output dependencies between tasks, constructing a Directed Acyclic Graph to support complex logic flows.
- **Self-Healing Code Execution**: Automatically captures runtime errors (Tracebacks), analyzes causes, and regenerates code, supporting up to 5 automatic retries.
- **Flexible LLM Configuration**: Supports independent LLM configuration for each Agent (e.g., OpenAI, DeepSeek, Ollama), optimizing cost and performance.
- **Method Library Integration**: Built-in **HMML (Hierarchical Mathematical Modeling Methods Library)** supports automatic retrieval of the most matching mathematical methods.
- **Multi-Environment Support**: Decoupled code execution layer supporting local Jupyter Kernel or cloud sandboxes (E2B, Daytona).
- **Real-time Progress Feedback**: Full-duplex communication based on WebSocket, pushing task status, intermediate results, and logs in real-time.

## 🛠️ Technology Stack

Fast-MM is built on a modern technology stack to ensure high performance and scalability:

- **Frontend Layer**:
    - **Vue 3**: Reactive UI component building
    - **TailwindCSS**: Modern atomic CSS styling
    - **WebSocket Client**: Real-time bidirectional communication

- **Backend Layer**:
    - **FastAPI**: High-performance async HTTP/WebSocket framework
    - **Python 3.10+**: Core runtime environment
    - **Uvicorn**: Production-grade ASGI server

- **Infrastructure**:
    - **Redis**: Task queue management & Pub/Sub message bus
    - **LiteLLM**: Unified LLM interface abstraction layer
    - **Jupyter Kernel**: Local Python code execution environment
    - **(Optional) E2B / Daytona**: Cloud secure code sandboxes

- **Data & Knowledge**:
    - **HMML.json**: Hierarchical Mathematical Modeling Methods Library
    - **Markdown Templates**: Standardized paper structure templates
    - **OpenAlex API**: Scholarly literature retrieval service

## 🏗️ Architecture & Flow

### System Processing Flow

1. **Task Submission (POST /api/v1/task)**: User uploads problem and data; backend creates a Task and pushes it to the Redis queue.
2. **Orchestration (Coordinator)**: `CoordinatorAgent` analyzes the problem, constructs a task DAG, and determines the sub-task execution order.
3. **Modeling (Modeler)**: `ModelerAgent` retrieves HMML based on sub-tasks, generates mathematical models, and self-corrects via the Actor-Critic loop.
4. **Solution (Coder)**: `CoderAgent` receives model definitions and generates/executes code in the sandbox environment. If errors occur, the Self-Healing mechanism triggers automatic repair.
5. **Writing (Writer)**: `WriterAgent` integrates all intermediate results (formulas, code, charts), calls OpenAlex to search for relevant literature, and generates the final paper based on templates.

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
