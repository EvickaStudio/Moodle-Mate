from moodlemate.markdown.converter import apply_custom_rules, convert


def test_convert_basic_html_to_markdown():
    """Test basic HTML elements conversion."""
    html = "<h1>Title</h1><p>Hello <strong>World</strong></p>"
    md = convert(html)
    assert "# Title" in md
    assert "**World**" in md


def test_convert_links_thoroughly():
    """
    Test various link scenarios including the recent fixes for Discord compatibility.
    """
    # 1. Normal link
    assert (
        convert('<a href="https://example.com">Example</a>')
        == "[Example](https://example.com)"
    )

    # 2. Link with title (title should be removed)
    assert (
        convert('<a href="https://example.com" title="My Title">Example</a>')
        == "[Example](https://example.com)"
    )

    # 3. URL as text (should be simplified to raw URL for Discord)
    html_url_as_text = '<a href="https://example.com">https://example.com</a>'
    assert convert(html_url_as_text) == "https://example.com"

    # 4. URL as text with title
    html_url_title = '<a href="https://example.com" title="https://example.com">https://example.com</a>'
    assert convert(html_url_title) == "https://example.com"

    # 5. Email link (should remain markdown [text](mailto:url))
    assert (
        convert('<a href="mailto:test@example.com">test@example.com</a>')
        == "[test@example.com](mailto:test@example.com)"
    )


def test_convert_formatting():
    """Test standard markdown formatting."""
    # Headings
    assert "# H1" in convert("<h1>H1</h1>")
    assert "## H2" in convert("<h2>H2</h2>")

    # Emphasis
    assert "_Italic_" in convert("<i>Italic</i>")
    assert "**Bold**" in convert("<b>Bold</b>")

    # Lists
    md_list = convert("<ul><li>Item 1</li><li>Item 2</li></ul>")
    assert "* Item 1" in md_list
    assert "* Item 2" in md_list
    assert "\n\n* Item 2" not in md_list


def test_cleaner_patterns():
    """Test regex cleaning patterns in apply_custom_rules."""
    # Navigation breadcrumbs
    text = "[Home](/) » [Course](/c) » Lesson"
    assert apply_custom_rules(text) == "Lesson"

    # Images (should all be removed)
    images = "![alt](x.png) Some text [![x](y)](z) [](/img.jpg)"
    assert apply_custom_rules(images) == "Some text"

    # Forum management links
    forum_links = "Some content\n[Forum abbestellen]\nMore footer info"
    assert apply_custom_rules(forum_links) == "Some content"

    forum_links_2 = "Discussion text\n[Diskussion im Forum zeigen]\nMore footer info"
    assert apply_custom_rules(forum_links_2) == "Discussion text"


def test_cleaner_whitespace():
    """Test whitespace and newline normalization."""
    # Multiple newlines
    text = "Line 1\n\n\n\nLine 2"
    assert apply_custom_rules(text) == "Line 1\n\nLine 2"

    # Multiple spaces
    text = "Too    many      spaces"
    assert apply_custom_rules(text) == "Too many spaces"

    # Trailing/leading whitespace
    text = "   \n   Surrounded   \n   "
    assert apply_custom_rules(text) == "Surrounded"


def test_cleaner_normalizes_spaced_pseudo_list():
    """Convert heading + spaced lines into compact markdown bullets."""
    text = (
        "Was Dich erwartet:\n\n"
        "Individuelle Gruendungsberatung\n\n"
        "Persoenliches Mentoring\n\n"
        "Workshops, Events und Networking"
    )
    cleaned = apply_custom_rules(text)
    assert "- Individuelle Gruendungsberatung" in cleaned
    assert "- Persoenliches Mentoring" in cleaned
    assert "- Workshops, Events und Networking" in cleaned


def test_cleaner_compacts_raw_bullet_list_spacing():
    """Collapse blank lines between bullet list items on raw markdown."""
    text = "* Item 1\n\n* Item 2\n\n* Item 3"
    cleaned = apply_custom_rules(text)
    assert cleaned == "* Item 1\n* Item 2\n* Item 3"


def test_cleaner_compacts_raw_numbered_list_spacing():
    """Collapse blank lines between numbered list items on raw markdown."""
    text = "1. Item 1\n\n2. Item 2\n\n3. Item 3"
    cleaned = apply_custom_rules(text)
    assert cleaned == "1. Item 1\n2. Item 2\n3. Item 3"


def test_cleaner_fixes_split_bold_email():
    """Remove broken bold markers split around an email line."""
    text = "Sende alle Unterlagen an: **info@example.com\n**Weitere Infos hier."
    cleaned = apply_custom_rules(text)
    assert "**" not in cleaned
    assert "info@example.com" in cleaned


def test_cleaner_preserves_non_email_multiline_bold():
    """Do not alter multiline bold text when it is not an email split."""
    text = "**Wichtiger Hinweis\n**Weitere Informationen folgen."
    cleaned = apply_custom_rules(text)
    assert cleaned == text


def test_cleaner_fixes_multiple_split_bold_email_segments():
    """Fix each split email-bold segment in the same text."""
    text = (
        "Kontakt A: **a@example.com\n**Infos A\n\n"
        "Kontakt B: **b@example.com\n**Infos B"
    )
    cleaned = apply_custom_rules(text)
    assert "**" not in cleaned
    assert "a@example.com\nInfos A" in cleaned
    assert "b@example.com\nInfos B" in cleaned
