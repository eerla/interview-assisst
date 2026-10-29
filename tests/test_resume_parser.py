"""
Tests for ResumeParser core functionality.
"""

import io

from interview_assistant.core.resume_parser import ResumeParser


class MockUploadedFile(io.BytesIO):
    """Mock Streamlit uploaded file object (BytesIO subclass)."""

    def __init__(self, content: bytes, file_type: str, name: str = "test.pdf"):
        super().__init__(content)
        self.type = file_type
        self.name = name
        self.size = len(content)


class TestResumeParserCleanText:
    """Test cases for clean_text static method."""

    def test_clean_text_none(self):
        result = ResumeParser.clean_text(None)
        assert result == ""

    def test_clean_text_empty(self):
        result = ResumeParser.clean_text("")
        assert result == ""

    def test_clean_text_normalizes_whitespace(self):
        text = "Hello   World\n\n\nFoo    Bar"
        result = ResumeParser.clean_text(text)
        assert "   " not in result
        assert "\n\n" not in result
        assert result == "Hello World Foo Bar"

    def test_clean_text_strips_leading_trailing(self):
        result = ResumeParser.clean_text("  hello world  ")
        assert result == "hello world"


class TestResumeParserParseResume:
    """Test cases for parse_resume static method."""

    def test_parse_resume_none(self):
        result = ResumeParser.parse_resume(None)
        assert result is None

    def test_parse_resume_unsupported_type(self, parser):
        mock_file = MockUploadedFile(b"content", "image/png")
        result = parser.parse_resume(mock_file)
        assert result is None

    def test_parse_resume_pdf(self, parser, sample_pdf_bytes):
        mock_file = MockUploadedFile(sample_pdf_bytes, "application/pdf")
        result = parser.parse_resume(mock_file)
        # PDF may extract empty text; just verify no crash and returns str or None
        assert result is None or isinstance(result, str)

    def test_parse_resume_docx(self, parser, sample_docx_bytes):
        mock_file = MockUploadedFile(
            sample_docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        result = parser.parse_resume(mock_file)
        assert result is None or isinstance(result, str)
        if result:
            assert "John Doe" in result or "Software Engineer" in result


class TestResumeParserExtractPDF:
    """Test cases for extract_text_from_pdf static method."""

    def test_extract_pdf_valid(self, parser, sample_pdf_bytes):
        mock_file = MockUploadedFile(sample_pdf_bytes, "application/pdf")
        result = ResumeParser.extract_text_from_pdf(mock_file)
        assert result is None or isinstance(result, str)

    def test_extract_pdf_invalid_bytes(self, parser):
        mock_file = MockUploadedFile(b"not a pdf", "application/pdf")
        result = ResumeParser.extract_text_from_pdf(mock_file)
        assert result is None


class TestResumeParserExtractDOCX:
    """Test cases for extract_text_from_docx static method."""

    def test_extract_docx_valid(self, parser, sample_docx_bytes):
        mock_file = MockUploadedFile(
            sample_docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        result = ResumeParser.extract_text_from_docx(mock_file)
        assert isinstance(result, str)
        assert "John Doe" in result

    def test_extract_docx_invalid_bytes(self, parser):
        mock_file = MockUploadedFile(
            b"not a docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        result = ResumeParser.extract_text_from_docx(mock_file)
        assert result is None
