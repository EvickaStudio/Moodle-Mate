import os
import shutil
import sys
import time
from typing import Iterable, List

from src.core.version import __version__

# ANSI escape codes for colors and effects
COLOR_BORDER = "\033[38;5;240m"
COLOR_MOODLE = "\033[38;5;9m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_FADE = "\033[2m"


def _compose_logo_lines() -> List[str]:
    """
    Build the colored ASCII logo lines.

    Returns:
        List[str]: The logo lines with ANSI colors applied.
    """
    header = (
        f"{COLOR_BORDER}╭─┐ {COLOR_RESET}{COLOR_BOLD}Moodle Mate"
        f" {COLOR_MOODLE}{__version__:>8}{COLOR_RESET} "
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


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def _center_lines(lines: Iterable[str]) -> List[str]:
    """
    Center lines based on the current terminal width.

    Args:
        lines (Iterable[str]): Lines to center.

    Returns:
        List[str]: Centered lines with left padding applied.
    """
    try:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
    except Exception:
        width = 80

    centered: List[str] = []
    for raw in lines:
        # Strip ANSI for length calculation to avoid mis-centering
        stripped = _strip_ansi(raw)
        pad = max(0, (width - len(stripped)) // 2)
        centered.append(" " * pad + raw)
    return centered


def _strip_ansi(s: str) -> str:
    """Remove ANSI escape codes for length computations."""
    import re

    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_re.sub("", s)


def _print_char_by_char(line: str, delay: float) -> None:
    """Print a line character-by-character with a small delay for smoothness."""
    for ch in line:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print("")


def animate_logo(animate: bool = True) -> None:
    """
    Render the startup logo with optional smooth animation and centering.

    Args:
        animate (bool): If True, reveal the logo smoothly; otherwise print instantly.
    """
    lines = _center_lines(_compose_logo_lines())

    if animate:
        # Subtle fade-in prelude
        for line in lines:
            print(f"{COLOR_FADE}{line}{COLOR_RESET}")
        time.sleep(0.12)
        # Replace with the final reveal
        # Move cursor up to re-draw in place
        sys.stdout.write(f"\033[{len(lines)}A")
        sys.stdout.flush()
        for line in lines:
            _print_char_by_char(line, delay=0.003)
            time.sleep(0.02)
    else:
        for line in lines:
            print(line)


def loading_animation(duration: float) -> None:
    """Display a simple loading spinner for the given duration (seconds)."""
    animation = "|/-\\"
    idx = 0
    end_time = time.time() + duration
    while time.time() < end_time:
        print(
            f"\r{COLOR_BOLD}Loading {animation[idx % len(animation)]}{COLOR_RESET}",
            end="",
            flush=True,
        )
        idx += 1
        time.sleep(0.08)
    print("\r" + " " * 32 + "\r", end="")


if __name__ == "__main__":
    clear_screen()
    loading_animation(1)
    animate_logo(animate=True)
    input(f"\n{COLOR_FADE}Press Enter to continue...{COLOR_RESET}")
