# grey
COLOR_BORDER = "\033[38;5;240m"
COLOR_MOODLE = "\033[38;5;9m"
RESET = "\033[0m"  # Reset to default

logo = f"""{COLOR_BORDER}╭─┐ {RESET}Moodle Mate {COLOR_BORDER}┌────────────────────────────────────────────────────────╮
│       {COLOR_MOODLE}__  ___             ____    {RESET}__  ___     __        ,-------,      {COLOR_BORDER}│
│      {COLOR_MOODLE}/  |/  /__  ___  ___/ / /__ {RESET}/  |/  /__ _/ /____   /       / |     {COLOR_BORDER}│
│     {COLOR_MOODLE}/ /|_/ / _ \/ _ \/ _  / / -_){RESET} /|_/ / _ `/ __/ -_) /______ /  /     {COLOR_BORDER}│
│    {COLOR_MOODLE}/_/  /_/\___/\___/\_,_/_/\__/{RESET}_/  /_/\_,_/\__/\__/ |___/___/  /      {COLOR_BORDER}│
│     {RESET}-—--–=¤=—--–-- - -  EvickaStudio  - - --–--—=¤=--|__..___|.'- -    {COLOR_BORDER}│
│                                                        {RESET}//              {COLOR_BORDER}│
╰────────────────────────────────────────────────────────────────────────╯{RESET}
"""

old_logo = """
   __  ___             ____    __  ___     __        ,-------,
  /  |/  /__  ___  ___/ / /__ /  |/  /__ _/ /____   /       / | 
 / /|_/ / _ \/ _ \/ _  / / -_) /|_/ / _ `/ __/ -_) /______ /  /
/_/  /_/\___/\___/\_,_/_/\__/_/  /_/\_,_/\__/\__/ |___/___/  /
 -—--–=¤=—--–-- - -  EvickaStudio  - - --–--—=¤=--|__..___|.'- -
                                                    //
"""


if __name__ == "__main__":
    import os

    cls = lambda: os.system("cls" if os.name == "nt" else "clear")
    cls()
    print(logo)
