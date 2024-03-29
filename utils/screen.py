# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

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


# Clear screen
def clear_screen() -> None:
    """
    Clears the terminal screen.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    cls = lambda: os.system("cls" if os.name == "nt" else "clear")
    cls()
    print(logo)
