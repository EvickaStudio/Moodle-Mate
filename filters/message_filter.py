# To be impelemented
# This file will contain different filter for moodle messages
# as the moodle notification that are fetched via the moodle api
# are plain html and contain a lot of unwanted information such as
# information about the course, forum, etc.

import logging

import bs4


def parse_html_to_text(html):
    """
    Parses the given HTML content to plain text.

    :param html: HTML content as a string.
    :return: Plain text after removing HTML tags.
    """
    try:
        # TODO: FIlter mehr ausbauen, die letzten 4 Zeilen braucht man nicht
        soup = bs4.BeautifulSoup(html, "html.parser")
        temp = "\n".join(
            [line.rstrip() for line in soup.get_text().splitlines() if line.strip()]
        )
        # remove lines with more then 3 whitespaces in the beginning
        temp = "\n".join(
            [line for line in temp.splitlines() if not line.startswith("   ")]
        )
        return "\n".join(
            temp.splitlines()[:-1]
        )  # removes the last line which is always the same
    except Exception as e:
        logging.exception("Failed to parse HTML")
        return None
