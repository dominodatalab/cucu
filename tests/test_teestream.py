from io import StringIO

import pytest_check as check

from cucu.utils import TeeStream


def test_teestream_writes_to_file_and_buffer():
    """Test that TeeStream writes to both file and internal buffer simultaneously."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    test_data = "Hello, World!"
    tee.write(test_data)

    # Check both outputs with soft assertions to see all results
    check.equal(file_stream.getvalue(), test_data, "File stream should contain the written data")
    check.equal(tee.getvalue(), test_data, "Buffer should contain the written data")


def test_teestream_multiple_writes():
    """Test that multiple sequential writes work correctly."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    tee.write("Line 1\n")
    tee.write("Line 2\n")
    tee.write("Line 3\n")

    expected = "Line 1\nLine 2\nLine 3\n"

    # Check both outputs with soft assertions
    check.equal(file_stream.getvalue(), expected, "File stream should contain all writes")
    check.equal(tee.getvalue(), expected, "Buffer should contain all writes")


def test_teestream_content_consistency():
    """Test that both file stream and buffer contain identical content."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    # Write multiple chunks of data
    chunks = ["First chunk", " Second chunk", " Third chunk"]
    for chunk in chunks:
        tee.write(chunk)

    # Verify both outputs are identical and contain expected content
    file_content = file_stream.getvalue()
    buffer_content = tee.getvalue()
    expected = "First chunk Second chunk Third chunk"
    
    check.equal(file_content, buffer_content, "File and buffer content should be identical")
    check.equal(file_content, expected, "Content should match expected concatenation")
