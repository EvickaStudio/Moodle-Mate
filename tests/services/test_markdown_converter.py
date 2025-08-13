from src.services.markdown.converter import clean_converted_text, convert


def test_convert_basic_html_to_markdown():
    html = "<h1>Title</h1><p>Hello <strong>World</strong></p>"
    md = convert(html)
    assert "# Title" in md
    assert "**World**" in md


def test_cleaner_removes_images_and_breadcrumbs():
    text = (
        "[Home](/) » [Course](/c) » Lesson\n"
        "![alt](x.png) Some text [![x](y)](z) [](/img.jpg)"
    )
    cleaned = clean_converted_text(text)
    assert "»" not in cleaned
    assert "![" not in cleaned
    assert "](/img.jpg)" not in cleaned
