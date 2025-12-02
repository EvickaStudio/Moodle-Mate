import shutil
from typing import Iterable, List

from src.core.version import __version__

# Original Color Palette (Restored)
COLOR_BORDER = "\033[38;5;240m"
COLOR_MOODLE = "\033[38;5;208m" # Orange/Moodle color
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

def _compose_logo_lines() -> List[str]:
    """
    Build the colored ASCII logo lines (Original Design).
    """
    version_str = f"{__version__:>8}"
    
    header = (
        f"{COLOR_BORDER}╭─┐ {COLOR_RESET}{COLOR_BOLD}Moodle Mate"
        f" {COLOR_MOODLE}{version_str}{COLOR_RESET} "
        f"{COLOR_BORDER}┌{'─' * 47}╮{COLOR_RESET}"
    )
    
    lines = [
        header,
        (
            f"{COLOR_BORDER}│       {COLOR_MOODLE}__  ___             ____    "
            f"{COLOR_RESET}__  ___     __        ,-------,      {COLOR_BORDER}│{COLOR_RESET}"
        ),
        (
            f"{COLOR_BORDER}│      {COLOR_MOODLE}/  |/  /__  ___  ___/ / /__ "
            f"{COLOR_RESET}/  |/  /__ _/ /____   /       / |     {COLOR_BORDER}│{COLOR_RESET}"
        ),
        (
            f"{COLOR_BORDER}│     {COLOR_MOODLE}/ /|_/ / _ \\ / _ \\ _  / / -_)"
            f"{COLOR_RESET} /|_/ / _ `/ __/ -_) /______ /  /     {COLOR_BORDER}│{COLOR_RESET}"
        ),
        (
            f"{COLOR_BORDER}│    {COLOR_MOODLE}/_/  /_/\\___/\\___/\\_,_/_/\\__/"
            f"{COLOR_RESET}_/  /_/\\_,_/\\__/\\__/ |___/___/  /      {COLOR_BORDER}│{COLOR_RESET}"
        ),
        (
            f"{COLOR_BORDER}│     {COLOR_RESET}-—--–=¤=—--–-- - -  {COLOR_BOLD}EvickaStudio"
            f"{COLOR_RESET}  - - --–--—=¤=--|__..___|.'- -    {COLOR_BORDER}│{COLOR_RESET}"
        ),
        (
            f"{COLOR_BORDER}│                                                        "
            f"{COLOR_RESET}//              {COLOR_BORDER}│{COLOR_RESET}"
        ),
        f"{COLOR_BORDER}╰{'─' * 72}╯{COLOR_RESET}",
    ]
    return lines

def _center_lines(lines: Iterable[str]) -> List[str]:
    """Center lines based on the current terminal width."""
    try:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
    except Exception:
        width = 80

    centered: List[str] = []
    for raw in lines:
        stripped = _strip_ansi(raw)
        pad = max(0, (width - len(stripped)) // 2)
        centered.append(" " * pad + raw)
    return centered

def _strip_ansi(s: str) -> str:
    """Remove ANSI escape codes."""
    import re
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_re.sub("", s)

def print_logo() -> None:
    """
    Render the logo instantly.
    """
    raw_lines = _compose_logo_lines()
    centered_lines = _center_lines(raw_lines)
    for line in centered_lines:
        print(line)

if __name__ == "__main__":
    print_logo()
