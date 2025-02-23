from src.service.formatting.html_cleaner import clean_html


def test_clean_html_removes_tags():
    raw_html = "<p>Hello, <strong>world</strong>!</p>"
    expected = "Hello, world!"
    assert clean_html(raw_html) == expected


def test_clean_html_no_tags():
    text = "Just plain text without HTML"
    assert clean_html(text) == text


def test_clean_html_empty_string():
    assert clean_html("") == ""


def test_clean_html_nested_tags():
    raw_html = "<div><p>Nested <span>text</span> inside tags</p></div>"
    expected = "Nested text inside tags"
    assert clean_html(raw_html) == expected


def test_clean_html_with_attributes():
    raw_html = '<a href="http://example.com" title="Example">Example Link</a>'
    expected = "Example Link"
    assert clean_html(raw_html) == expected
