import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import modeling_router, ws_router, common_router, files_router, mcp
from .services.mcp_manager import mcp_manager
from .utils.log_util import logger
from .utils.cli import print_banner


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用生命周期管理
    启动阶段：打印 banner、记录启动日志、创建项目目录
    关闭阶段：记录停止日志
    """
    print_banner()
    logger.info("Starting Fast-MM")
    os.makedirs("./project", exist_ok=True)
    
    # Initialize MCP Manager
    await mcp_manager.initialize()
    
    yield
    
    # Cleanup MCP Manager
    await mcp_manager.cleanup()
    
    logger.info("Stopping Fast-MM")


app = FastAPI(
    title="Fast-MM",
    description="Agents for Fast-MM",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(modeling_router.router)
app.include_router(ws_router.router)
app.include_router(common_router.router)
app.include_router(files_router.router)
app.include_router(mcp.router)


# 跨域 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # 暴露所有响应头
)

app.mount(
    "/static",  # 这是访问时的前缀
    StaticFiles(directory="project/work_dir"),  # 这是本地文件夹路径
    name="static",
)
