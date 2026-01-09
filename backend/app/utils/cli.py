from textwrap import dedent

def center_cli_str(text: str, width: int | None = None):
    import shutil

    width = width or shutil.get_terminal_size().columns
    lines = text.split("\n")
    max_line_len = max(len(line) for line in lines)
    return "\n".join(
        (line + " " * (max_line_len - len(line))).center(width) for line in lines
    )


def get_ascii_banner(center: bool = True) -> str:
    text = dedent(
        r"""
        ========================================================================

                ███████╗ █████╗ ███████╗████████╗   ███╗   ███╗███╗   ███╗
                ██╔════╝██╔══██╗██╔════╝╚══██╔══╝   ████╗ ████║████╗ ████║
                █████╗  ███████║███████╗   ██║█████╗██╔████╔██║██╔████╔██║
                ██╔══╝  ██╔══██║╚════██║   ██║╚════╝██║╚██╔╝██║██║╚██╔╝██║
                ██║     ██║  ██║███████║   ██║      ██║ ╚═╝ ██║██║ ╚═╝ ██║
                ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝      ╚═╝     ╚═╝╚═╝     ╚═╝           
                                            
        ========================================================================
        """,
    ).strip()
    if center:
        return center_cli_str(text)
    else:
        return text
