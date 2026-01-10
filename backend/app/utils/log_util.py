import sys
import contextvars
from pathlib import Path
from loguru import logger as LOGGER
from .cli import HAS_RICH, console

if HAS_RICH:
    from rich.logging import RichHandler

# 定义 contextvar 用于存储 trace_id（支持协程/多线程安全传递）
trace_id_ctx = contextvars.ContextVar("trace_id", default="unknown-trace-id")


class LoggerInitializer:
    """
    Loguru 日志初始化工具类（单例模式）
    功能：配置控制台日志输出 + 按日/按大小轮转的错误日志文件输出
    """
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_ERROR_LOG_SUFFIX = "_error.log"
    DEFAULT_ROTATION_SIZE = "50MB"
    DEFAULT_RETENTION_DAYS = "7 days"
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_COMPRESSION = "zip"
    _instance = None

    def __new__(cls, *args, **kwargs):
        """实现单例模式，确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, log_dir: str = None):
        """
        初始化日志目录（若已实例化，重复调用不重新初始化）
        :param log_dir: 自定义日志目录，默认使用 DEFAULT_LOG_DIR
        """
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.log_dir = Path(log_dir or self.DEFAULT_LOG_DIR).resolve()
        self.error_log_path = self.log_dir / f"{{time:YYYY-MM-DD}}{self.DEFAULT_ERROR_LOG_SUFFIX}"
        self._create_log_dir()
        self._initialized = True

    def _create_log_dir(self):
        """创建日志目录，捕获权限不足等异常"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            LOGGER.debug(f"Successfully created log directory: {self.log_dir}")
        except PermissionError:
            raise PermissionError(f"Permission denied: Unable to create log directory: {self.log_dir}")
        except Exception as e:
            raise Exception(f"Failed to create log directory: {str(e)}") from e

    def _filter(self, log: dict) -> bool:
        """
        自定义日志过滤器：注入 trace_id 到日志记录中
        :param log: loguru 传入的日志字典
        :return: 是否保留该日志（True=保留，False=丢弃）
        """
        log["extra"]["trace_id"] = trace_id_ctx.get()
        return True

    def init(self):
        """
        初始化 loguru 日志配置（控制台 + 文件输出）
        特点：异步写入、自动轮转、自动压缩、保留7天日志
        """
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<magenta>{extra[trace_id]}</magenta> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        # 移除 loguru 默认的控制台输出配置
        LOGGER.remove()

        if HAS_RICH and console:
            # 使用 RichHandler 提供现代化的 CLI 体验
            # 简化格式，因为 RichHandler 已经提供了时间、等级和路径
            # 注意：RichHandler 使用 [] 语法而不是 loguru 的 <> 语法
            # trace_id 如果包含连字符可能会被误认为是 Rich 标签，因此添加转义
            rich_format = "[magenta]\\[{extra[trace_id]}][/magenta] {message}"
            
            LOGGER.add(
                RichHandler(
                    console=console, 
                    show_time=True, 
                    omit_repeated_times=False,
                    show_level=True, 
                    show_path=True,
                    rich_tracebacks=True,
                    markup=True
                ),
                filter=self._filter,
                format=rich_format,
                level="INFO",
                enqueue=True
            )
        else:
            # 降级到标准输出
            LOGGER.add(sys.stderr, filter=self._filter, format=log_format, enqueue=True)  # noqa

        LOGGER.add(
            self.error_log_path,
            filter=self._filter,  # noqa
            format=log_format,
            rotation=self.DEFAULT_ROTATION_SIZE,
            retention=self.DEFAULT_RETENTION_DAYS,
            encoding=self.DEFAULT_ENCODING,
            enqueue=True,
            compression=self.DEFAULT_COMPRESSION,
        )

        return LOGGER


log_initializer = LoggerInitializer()
logger = log_initializer.init()