class Style:
    TEXT_MOODLE = "\033[38;2;244;128;32m"
    TEXT_MATE = "\x1b[0m"


LOGO = [
    ["█▀▄▀█ █▀▀█ █▀▀█ █▀▀▄ █   █▀▀ ", "█▀▄▀█ █▀▀█ ▀▀█▀▀ █▀▀"],
    ["█░▀░█ █░░█ █░░█ █░░█ █░░ █▀▀ ", "█░▀░█ █▄▄█   █   █▀▀"],
    ["▀   ▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀  ▀▀▀ ▀▀▀ ", "▀   ▀ ▀  ▀   ▀   ▀▀▀"],
]


def get_logo(pad: str = "") -> str:
    result: list[str] = []
    result.extend(
        f"{pad}{Style.TEXT_MOODLE}{row[0]}{Style.TEXT_MATE}{row[1]}" for row in LOGO
    )
    return "\n".join(result)


def main() -> None:
    print(get_logo())


if __name__ == "__main__":
    main()
