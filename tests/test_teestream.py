import tempfile
from io import StringIO

from cucu.utils import TeeStream


def test_teestream_writes_to_file_and_buffer():
    """Test that TeeStream writes to both file and internal buffer."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as temp_file:
        tee = TeeStream(temp_file)

        test_data = "Hello, World!"
        tee.write(test_data)
        tee.flush()

        # Check that data was written to file
        temp_file.seek(0)
        file_content = temp_file.read()
        assert file_content == test_data

        # Check that data was captured in buffer
        buffer_content = tee.getvalue()
        assert buffer_content == test_data


def test_teestream_multiple_writes():
    """Test that TeeStream handles multiple writes correctly."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    tee.write("Line 1\n")
    tee.write("Line 2\n")
    tee.write("Line 3\n")

    expected = "Line 1\nLine 2\nLine 3\n"

    # Check file content
    assert file_stream.getvalue() == expected

    # Check buffer content
    assert tee.getvalue() == expected


def test_teestream_read_alias():
    """Test that read() is an alias for getvalue()."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    test_data = "Test data"
    tee.write(test_data)

    assert tee.read() == test_data
    assert tee.getvalue() == test_data


def test_teestream_clear_buffer():
    """Test that clear() resets the internal buffer."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    tee.write("Initial data")
    assert tee.getvalue() == "Initial data"

    tee.clear()
    assert tee.getvalue() == ""

    # File content should still be there
    assert file_stream.getvalue() == "Initial data"

    # New writes should work normally
    tee.write("New data")
    assert tee.getvalue() == "New data"
    assert file_stream.getvalue() == "Initial dataNew data"


def test_teestream_empty_writes():
    """Test that TeeStream handles empty writes."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    tee.write("")
    assert tee.getvalue() == ""
    assert file_stream.getvalue() == ""


def test_teestream_flush():
    """Test that flush() calls flush on the file stream."""
    file_stream = StringIO()
    tee = TeeStream(file_stream)

    tee.write("Test")
    tee.flush()  # Should not raise any exceptions

    assert tee.getvalue() == "Test"
    assert file_stream.getvalue() == "Test"


def test_teestream_with_real_file():
    """Test TeeStream with an actual file object."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as temp_file:
        tee = TeeStream(temp_file)

        lines = ["First line\n", "Second line\n", "Third line\n"]
        for line in lines:
            tee.write(line)

        tee.flush()

        # Read from file
        temp_file.seek(0)
        file_lines = temp_file.readlines()
        assert file_lines == lines

        # Check buffer
        expected_buffer = "".join(lines)
        assert tee.getvalue() == expected_buffer
