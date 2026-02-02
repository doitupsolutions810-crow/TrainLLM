# Seed Platform v10.x Docs Testing Approach

## Component Overview

[`seed-platform-v10x-docs/`](../seed-platform-v10x-docs) is a Python documentation generation project:
- [`generate_docs.py`](../seed-platform-v10x-docs/generate_docs.py) - Main script that converts markdown to HTML
- Reads markdown files ([`QUICKSTART.md`](../seed-platform-v10x-docs/QUICKSTART.md), [`USAGE_GUIDE.md`](../seed-platform-v10x-docs/USAGE_GUIDE.md))
- Generates single-page HTML documentation site
- Adds unique IDs to prevent anchor conflicts
- Generates navigation menu from headers
- Designed to run in GitHub Actions

## Testing Challenges

1. **File I/O**: Script reads and writes files
2. **External Dependencies**: Uses `markdown` library
3. **String Manipulation**: Complex regex for ID/href prefixing
4. **HTML Generation**: Large HTML template with embedded CSS
5. **Error Handling**: File not found, conversion errors
6. **No Business Logic**: Primarily utility/conversion functions

## Testing Strategy

### Testing Approach

We'll use `pytest` to:
- Test file reading with various scenarios
- Test markdown to HTML conversion
- Test ID/href prefixing logic
- Test navigation generation
- Test error handling
- Test HTML template generation
- Mock file system operations

### Test File Structure

```
seed-platform-v10x-docs/tests/
├── __init__.py
├── conftest.py                      # Shared fixtures
├── test_generate_docs.py          # Main script tests
└── test_utils/                     # Utility function tests
    ├── __init__.py
    ├── test_file_operations.py
    ├── test_markdown_conversion.py
    ├── test_prefix_logic.py
    └── test_html_generation.py
```

## Detailed Test Cases

### Test Suite 1: File Operations

#### Test 1.1: read_file reads existing file

```python
import pytest
from pathlib import Path
from generate_docs import read_file

def test_read_file_existing(tmp_path):
    """Test reading an existing file"""
    # Create test file
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test Content")
    
    content = read_file(str(test_file))
    
    assert content is not None
    assert "# Test Content" in content
```

#### Test 1.2: read_file returns None for non-existent file

```python
def test_read_file_not_found(tmp_path):
    """Test reading a non-existent file"""
    content = read_file("nonexistent.md")
    
    assert content is None
```

#### Test 1.3: read_file handles empty file

```python
def test_read_file_empty_file(tmp_path):
    """Test reading an empty file"""
    test_file = tmp_path / "empty.md"
    test_file.write_text("")
    
    content = read_file(str(test_file))
    
    assert content == ""
```

#### Test 1.4: read_file handles unicode content

```python
def test_read_file_unicode(tmp_path):
    """Test reading file with unicode content"""
    test_file = tmp_path / "unicode.md"
    test_file.write_text("Hello 世界 🌍")
    
    content = read_file(str(test_file))
    
    assert "Hello 世界 🌍" in content
```

### Test Suite 2: Markdown Conversion

#### Test 2.1: convert_markdown_to_html converts basic markdown

```python
from generate_docs import convert_markdown_to_html

def test_convert_basic_markdown():
    """Test converting basic markdown to HTML"""
    md_content = "# Heading\n\nParagraph text."
    
    html = convert_markdown_to_html(md_content)
    
    assert html is not None
    assert "<h1" in html
    assert "<p>Paragraph text.</p>" in html
```

#### Test 2.2: convert_markdown_to_html with code blocks

```python
def test_convert_markdown_with_code():
    """Test converting markdown with code blocks"""
    md_content = "```python\nprint('hello')\n```"
    
    html = convert_markdown_to_html(md_content)
    
    assert html is not None
    assert "<code>" in html
    assert "print('hello')" in html
```

#### Test 2.3: convert_markdown_to_html with tables

```python
def test_convert_markdown_with_tables():
    """Test converting markdown with tables"""
    md_content = "| Header 1 | Header 2 |\n| Cell 1 | Cell 2 |"
    
    html = convert_markdown_to_html(md_content)
    
    assert html is not None
    assert "<table>" in html
```

#### Test 2.4: convert_markdown_to_html handles conversion errors

```python
def test_convert_markdown_error_handling():
    """Test error handling in markdown conversion"""
    # Mock markdown to raise error
    import markdown
    original_markdown = markdown.markdown
    
    def mock_markdown_error(*args, **kwargs):
        raise Exception("Conversion error")
    
    markdown.markdown = mock_markdown_error
    
    html = convert_markdown_to_html("# Test")
    
    assert html is None
    
    # Restore original
    markdown.markdown = original_markdown
```

### Test Suite 3: ID Prefix Logic

#### Test 3.1: add_id_prefix adds prefix to all IDs

```python
from generate_docs import add_id_prefix

def test_add_id_prefix():
    """Test adding prefix to all ID attributes"""
    html = '<h1 id="test">Heading</h1><h2 id="another">Subheading</h2>'
    
    result = add_id_prefix(html, 'prefix-')
    
    assert 'id="prefix-test"' in result
    assert 'id="prefix-another"' in result
```

#### Test 3.2: add_id_prefix handles multiple IDs

```python
def test_add_id_prefix_multiple():
    """Test adding prefix to multiple ID attributes"""
    html = '<div id="one"></div><div id="two"></div><div id="three"></div>'
    
    result = add_id_prefix(html, 'section-')
    
    assert 'id="section-one"' in result
    assert 'id="section-two"' in result
    assert 'id="section-three"' in result
```

#### Test 3.3: add_id_prefix handles no IDs

```python
def test_add_id_prefix_no_ids():
    """Test adding prefix when no IDs present"""
    html = '<h1>Heading</h1><p>Paragraph</p>'
    
    result = add_id_prefix(html, 'prefix-')
    
    assert result == html  # No change
```

#### Test 3.4: add_id_prefix handles empty prefix

```python
def test_add_id_prefix_empty():
    """Test adding empty prefix"""
    html = '<h1 id="test">Heading</h1>'
    
    result = add_id_prefix(html, '')
    
    assert 'id="test"' in result  # Prefix is empty but still added
```

### Test Suite 4: Href Prefix Logic

#### Test 4.1: add_href_prefix adds prefix to all hrefs

```python
from generate_docs import add_href_prefix

def test_add_href_prefix():
    """Test adding prefix to all href anchors"""
    html = '<a href="#section1">Link 1</a><a href="#section2">Link 2</a>'
    
    result = add_href_prefix(html, 'prefix-')
    
    assert 'href="#prefix-section1"' in result
    assert 'href="#prefix-section2"' in result
```

#### Test 4.2: add_href_prefix handles multiple hrefs

```python
def test_add_href_prefix_multiple():
    """Test adding prefix to multiple href attributes"""
    html = '<a href="#one">1</a><a href="#two">2</a><a href="#three">3</a>'
    
    result = add_href_prefix(html, 'section-')
    
    assert 'href="#section-one"' in result
    assert 'href="#section-two"' in result
    assert 'href="#section-three"' in result
```

#### Test 4.3: add_href_prefix handles no hrefs

```python
def test_add_href_prefix_no_href():
    """Test adding prefix when no hrefs present"""
    html = '<a href="https://example.com">External Link</a>'
    
    result = add_href_prefix(html, 'prefix-')
    
    assert result == html  # No change for external links
```

### Test Suite 5: Navigation Generation

#### Test 5.1: generate_navigation extracts h2 headers

```python
from generate_docs import generate_navigation

def test_generate_navigation_h2():
    """Test navigation generation extracts h2 headers"""
    html = '<h2 id="section1">Section 1</h2><h2 id="section2">Section 2</h2>'
    
    nav = generate_navigation(html, '')
    
    assert 'Section 1' in nav
    assert 'Section 2' in nav
```

#### Test 5.2: generate_navigation extracts h3 headers

```python
def test_generate_navigation_h3():
    """Test navigation generation extracts h3 headers"""
    html = '<h3 id="sub1">Subsection 1</h3><h3 id="sub2">Subsection 2</h3>'
    
    nav = generate_navigation(html, '')
    
    assert 'Subsection 1' in nav
    assert 'Subsection 2' in nav
```

#### Test 5.3: generate_navigation creates correct links

```python
def test_generate_navigation_links():
    """Test navigation creates correct anchor links"""
    html = '<h2 id="test-section">Test Section</h2>'
    
    nav = generate_navigation(html, '')
    
    assert '<a href="#test-section"' in nav
```

#### Test 5.4: generate_navigation handles empty HTML

```python
def test_generate_navigation_empty():
    """Test navigation generation with empty HTML"""
    html = ''
    
    nav = generate_navigation(html, '')
    
    assert nav == ''
```

### Test Suite 6: HTML Template Generation

#### Test 6.1: generate_html_template creates valid HTML

```python
from generate_docs import generate_html_template

def test_generate_html_template_structure():
    """Test HTML template has valid structure"""
    nav = '<nav>Test Navigation</nav>'
    content = '<div>Test Content</div>'
    
    html = generate_html_template(nav, content)
    
    assert '<!DOCTYPE html>' in html
    assert '<html' in html
    assert '<head>' in html
    assert '<body>' in html
    assert '</html>' in html
```

#### Test 6.2: generate_html_template includes navigation

```python
def test_generate_html_template_includes_nav():
    """Test HTML template includes navigation"""
    nav = '<nav>Test Navigation</nav>'
    content = '<div>Test Content</div>'
    
    html = generate_html_template(nav, content)
    
    assert 'Test Navigation' in html
    assert '<div class="sidebar">' in html
```

#### Test 6.3: generate_html_template includes content

```python
def test_generate_html_template_includes_content():
    """Test HTML template includes content"""
    nav = '<nav>Test Navigation</nav>'
    content = '<div>Test Content</div>'
    
    html = generate_html_template(nav, content)
    
    assert 'Test Content' in html
    assert '<div class="main-content">' in html
```

#### Test 6.4: generate_html_template includes CSS

```python
def test_generate_html_template_includes_css():
    """Test HTML template includes CSS styles"""
    nav = '<nav>Test</nav>'
    content = '<div>Content</div>'
    
    html = generate_html_template(nav, content)
    
    assert '<style>' in html
    assert 'font-family:' in html
    assert 'background:' in html
```

### Test Suite 7: Main Function

#### Test 7.1: main function runs successfully

```python
from generate_docs import main
from unittest.mock import patch, Mock
import sys
from io import StringIO

def test_main_success(tmp_path):
    """Test main function runs successfully"""
    # Create test markdown files
    quickstart = tmp_path / "QUICKSTART.md"
    usage = tmp_path / "USAGE_GUIDE.md"
    
    quickstart.write_text("# Quick Start\n\nContent here")
    usage.write_text("# Usage Guide\n\nContent here")
    
    # Mock stdout to capture output
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Change to test directory
    import os
    original_dir = os.getcwd()
    os.chdir(str(tmp_path))
    
    try:
        main()
    finally:
        os.chdir(original_dir)
        sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    
    assert "✅ Read QUICKSTART.md" in output
    assert "✅ Read USAGE_GUIDE.md" in output
    assert "✅ Markdown converted successfully" in output
```

#### Test 7.2: main function handles missing files

```python
def test_main_missing_files(tmp_path):
    """Test main function handles missing markdown files"""
    # Don't create markdown files
    
    # Mock stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Change to test directory
    import os
    original_dir = os.getcwd()
    os.chdir(str(tmp_path))
    
    try:
        main()
    finally:
        os.chdir(original_dir)
        sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    
    assert "❌ Failed to read required markdown files" in output
```

#### Test 7.3: main function generates index.html

```python
def test_main_generates_index(tmp_path):
    """Test main function generates index.html"""
    # Create test markdown files
    quickstart = tmp_path / "QUICKSTART.md"
    usage = tmp_path / "USAGE_GUIDE.md"
    
    quickstart.write_text("# Test")
    usage.write_text("# Test")
    
    # Mock stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Change to test directory
    import os
    original_dir = os.getcwd()
    os.chdir(str(tmp_path))
    
    try:
        main()
    finally:
        os.chdir(original_dir)
        sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    
    assert "📝 Generating final HTML document" in output
```

### Test Suite 8: Integration Tests

#### Test 8.1: End-to-end workflow

```python
def test_end_to_end_workflow(tmp_path):
    """Test complete workflow from markdown to HTML"""
    # Create test markdown files
    quickstart = tmp_path / "QUICKSTART.md"
    usage = tmp_path / "USAGE_GUIDE.md"
    
    quickstart.write_text("# Quick Start\n\n## Section 1\nContent here\n\n## Section 2\nMore content")
    usage.write_text("# Usage Guide\n\n## Getting Started\nInstructions here")
    
    # Mock stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Change to test directory
    import os
    original_dir = os.getcwd()
    os.chdir(str(tmp_path))
    
    try:
        main()
    finally:
        os.chdir(original_dir)
        sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    
    # Verify all steps completed
    assert "✅ Read QUICKSTART.md" in output
    assert "✅ Read USAGE_GUIDE.md" in output
    assert "✅ Markdown converted successfully" in output
    assert "🗺️  Generating navigation" in output
    assert "📝 Generating final HTML document" in output
    
    # Verify HTML file was created
    index_file = tmp_path / "index.html"
    assert index_file.exists()
    
    # Verify HTML content
    html_content = index_file.read_text()
    assert "<!DOCTYPE html>" in html_content
    assert "Quick Start" in html_content
    assert "Usage Guide" in html_content
```

#### Test 8.2: ID uniqueness across sections

```python
def test_id_uniqueness(tmp_path):
    """Test that IDs are unique across sections"""
    # Create markdown with same section names
    quickstart = tmp_path / "QUICKSTART.md"
    usage = tmp_path / "USAGE_GUIDE.md"
    
    quickstart.write_text("# Introduction\n\nContent")
    usage.write_text("# Introduction\n\nContent")
    
    # Mock stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Change to test directory
    import os
    original_dir = os.getcwd()
    os.chdir(str(tmp_path))
    
    try:
        main()
    finally:
        os.chdir(original_dir)
        sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    
    # Verify HTML file was created
    index_file = tmp_path / "index.html"
    html_content = index_file.read_text()
    
    # Count occurrences of each ID
    import re
    id_pattern = r'id="([^"]*)"'
    ids = re.findall(id_pattern, html_content)
    
    # Should have unique IDs with prefixes
    assert len(ids) == 2  # One from each section
    assert 'quickstart-Introduction' in ids
    assert 'usage-Introduction' in ids
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=generate_docs
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### requirements-test.txt

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

## Running Tests

```bash
cd seed-platform-v10x-docs

# Run all tests
pytest

# Run with coverage
pytest --cov=generate_docs --cov-report=html

# Run specific test file
pytest tests/test_generate_docs.py

# Run specific test
pytest tests/test_generate_docs.py -k "test_read_file_existing"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run excluding slow tests
pytest -m "not slow"
```

## Coverage Goals

- **Statement Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

## Testing Best Practices Applied

1. **Fixtures**: Use `tmp_path` fixture for file operations
2. **Isolation**: Each test is independent
3. **Mocking**: Mock stdout for main function testing
4. **AAA Pattern**: Arrange, Act, Assert structure
5. **Descriptive Names**: Test names clearly describe behavior
6. **Edge Cases**: Test empty files, unicode, errors
7. **Integration Tests**: Test complete workflows
8. **Coverage**: Automated coverage reporting with thresholds
9. **Error Handling**: Test both success and failure paths
10. **Regex Testing**: Verify ID/href prefixing logic

## Notes

- This is a utility script with minimal business logic
- Primary focus is on file I/O and string manipulation
- Testing focuses on:
  - File reading with various scenarios
  - Markdown to HTML conversion
  - ID/href prefixing to prevent conflicts
  - Navigation generation from headers
  - HTML template generation
  - Error handling for missing files
- The script is designed to run in GitHub Actions
- Tests use `tmp_path` fixture for isolated file operations
- `sys.stdout` is mocked to capture console output
- Unicode content is tested to ensure proper handling
- Complex regex patterns are tested for ID/href extraction
