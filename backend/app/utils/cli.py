import shutil
import platform
from textwrap import dedent

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich import box
    from rich.table import Table
    from rich.theme import Theme
    HAS_RICH = True

    OPENCODE_THEME = Theme({
        "info": "bold blue",
        "warning": "bold yellow",
        "error": "bold red",
        "success": "bold green",
        "highlight": "bold cyan",
        "dim": "dim white"
    })

    # 全局 Console 实例
    console = Console(theme=OPENCODE_THEME)

except ImportError:
    HAS_RICH = False
    console = None



ASCII_ART = dedent(r"""
    ███████╗ █████╗ ███████╗████████╗   ███╗   ███╗███╗   ███╗
    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝   ████╗ ████║████╗ ████║
    █████╗  ███████║███████╗   ██║█████╗██╔████╔██║██╔████╔██║
    ██╔══╝  ██╔══██║╚════██║   ██║╚════╝██║╚██╔╝██║██║╚██╔╝██║
    ██║     ██║  ██║███████║   ██║      ██║ ╚═╝ ██║██║ ╚═╝ ██║
    ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝      ╚═╝     ╚═╝╚═╝     ╚═╝
    """).strip()


def center_cli_str(text: str, width: int | None = None):
    width = width or shutil.get_terminal_size().columns
    lines = text.split("\n")
    max_line_len = max(len(line) for line in lines) if lines else 0
    return "\n".join(
        (line + " " * (max_line_len - len(line))).center(width) for line in lines
    )

def get_ascii_banner(center: bool = True) -> str:
    return center_cli_str(ASCII_ART) if center else ASCII_ART

def print_banner():
    """
    使用 Rich 打印美观的 Banner
    """
    if not HAS_RICH:
        print(get_ascii_banner())
        print(center_cli_str("GitHub: https://github.com/bluemoon-o2/Fast-MM"))
        return

    console = Console()

    # 创建带颜色的 Text 对象 (模拟垂直渐变)
    logo_text = Text()
    colors = ["bright_cyan", "cyan", "dodger_blue1", "dodger_blue2", "blue", "blue"]
    for i, line in enumerate(ASCII_ART.split("\n")):
        color = colors[i] if i < len(colors) else "blue"
        logo_text.append(line + "\n", style=f"bold {color}")
    
    # 构建信息表格
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(justify="right", style="bold yellow")
    info_table.add_column(justify="left", style="white")
    
    info_table.add_row("Version:", "2.0.0")
    info_table.add_row("Python:", platform.python_version())
    info_table.add_row("OS:", f"{platform.system()} {platform.release()}")
    info_table.add_row("GitHub:", "https://github.com/bluemoon-o2/Fast-MM")
    
    # 外层面板的内容网格
    grid = Table.grid(padding=1)
    grid.add_row(logo_text)
    grid.add_row("")
    grid.add_row(Align.center(info_table))

    panel = Panel(
        Align.center(grid),
        box=box.ROUNDED,
        border_style="blue",
        title="[bold green]Fast-MM Agent System[/bold green]",
        subtitle="[italic]Powered by FastAPI & LLMs[/italic]",
        width=80,
        padding=(1, 2)
    )

    console.print()
    console.print(Align.center(panel))
    console.print()
