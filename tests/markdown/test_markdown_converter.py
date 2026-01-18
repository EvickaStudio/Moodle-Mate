from moodlemate.markdown.converter import clean_converted_text, convert


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


def test_cleaner_patterns():
    """Test regex cleaning patterns in clean_converted_text."""
    # Navigation breadcrumbs
    text = "[Home](/) » [Course](/c) » Lesson"
    assert clean_converted_text(text) == "Lesson"

    # Images (should all be removed)
    images = "![alt](x.png) Some text [![x](y)](z) [](/img.jpg)"
    assert clean_converted_text(images) == "Some text"

    # Forum management links
    forum_links = "Some content\n[Forum abbestellen]\nMore footer info"
    assert clean_converted_text(forum_links) == "Some content"

    forum_links_2 = "Discussion text\n[Diskussion im Forum zeigen]\nMore footer info"
    assert clean_converted_text(forum_links_2) == "Discussion text"


def test_cleaner_whitespace():
    """Test whitespace and newline normalization."""
    # Multiple newlines
    text = "Line 1\n\n\n\nLine 2"
    assert clean_converted_text(text) == "Line 1\n\nLine 2"

    # Multiple spaces
    text = "Too    many      spaces"
    assert clean_converted_text(text) == "Too many spaces"

    # Trailing/leading whitespace
    text = "   \n   Surrounded   \n   "
    assert clean_converted_text(text) == "Surrounded"
