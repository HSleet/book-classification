from dataclasses import dataclass
from pathlib import Path
from functools import cached_property
from typing import Optional, Dict
import sys
import logging
import re

import pypdf
import ebooklib
from ebooklib import epub

logger = logging.getLogger(__name__)

_ISBN_RE = re.compile(
    r'\b(?:ISBN(?:-1[03])?:?\s*)?'
    r'((?:97[89][-\s]?\d{1,5}[-\s]?\d+[-\s]?\d+[-\s]?\d)|(?:\d{1,5}[-\s]?\d+[-\s]?\d+[-\s]?[0-9Xx]))\b'
)


def _normalize_isbn(raw: str) -> str:
    return re.sub(r'[^0-9Xx]', '', raw).upper()


@dataclass
class Book:
    filepath: Path

    def __post_init__(self):
        self.filepath = Path(self.filepath)

    def __str__(self) -> str:
        return f"{self.title or 'Unknown'} ({self.format})"

    def __repr__(self) -> str:
        return f"Book(filepath={self.filepath})"

    @cached_property
    def format(self) -> str:
        formats = {'.pdf': 'PDF', '.epub': 'EPUB'}
        return formats.get(self.filepath.suffix.lower(), 'Unknown')

    @cached_property
    def metadata(self) -> Dict[str, Optional[str]]:
        extractors = {'PDF': self._extract_pdf_metadata, 'EPUB': self._extract_epub_metadata}
        return extractors.get(self.format, lambda: {})()

    @cached_property
    def title(self) -> Optional[str]:
        return self.metadata.get('title')

    @cached_property
    def author(self) -> Optional[str]:
        return self.metadata.get('author')

    @cached_property
    def isbn(self) -> Optional[str]:
        extractors = {'PDF': self._extract_isbn_from_pdf, 'EPUB': self._extract_isbn_from_epub}
        return extractors.get(self.format, lambda: None)()

    def _extract_pdf_metadata(self) -> Dict[str, Optional[str]]:
        try:
            reader = pypdf.PdfReader(str(self.filepath))
            info = reader.metadata or {}
            get = lambda k: info.get(k) if isinstance(info, dict) else getattr(info, k, None)
            return {'title': get('/Title') or get('title'), 'author': get('/Author') or get('author')}
        except Exception as exc:
            logger.debug("PDF metadata error: %s", exc)
            return {}

    def _extract_epub_metadata(self) -> Dict[str, Optional[str]]:
        try:
            book = epub.read_epub(str(self.filepath))
            meta = lambda name: (book.get_metadata('DC', name) or [None])[0][0] if book.get_metadata('DC', name) else None
            return {'title': meta('title'), 'author': meta('creator')}
        except Exception as exc:
            logger.debug("EPUB metadata error: %s", exc)
            return {}

    def _extract_isbn_from_pdf(self, max_pages: int = 10) -> Optional[str]:
        try:
            reader = pypdf.PdfReader(str(self.filepath))
            for page in reader.pages[:max_pages]:
                isbn = self._find_isbn_in_text(page.extract_text() or '')
                if isbn:
                    return isbn
        except Exception as exc:
            logger.debug("PDF ISBN error: %s", exc)
        return None

    def _extract_isbn_from_epub(self) -> Optional[str]:
        try:
            book = epub.read_epub(str(self.filepath))
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                text = item.get_content().decode('utf-8', errors='ignore')
                isbn = self._find_isbn_in_text(text)
                if isbn:
                    return isbn
        except Exception as exc:
            logger.debug("EPUB ISBN error: %s", exc)
        return None

    @staticmethod
    def _find_isbn_in_text(text: str) -> Optional[str]:
        match = _ISBN_RE.search(text)
        return _normalize_isbn(match.group(1)) if match else None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python book_classificator.py <path_to_book>")
        sys.exit(1)

    book_path = Path(sys.argv[1])
    if not book_path.exists():
        print(f"File not found: {book_path}")
        sys.exit(1)
    
    if not book_path.is_file():
        print(f"Not a file: {book_path}")
        sys.exit(1)

    book = Book(book_path)
    print(f"Book: {book}")
    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"ISBN: {book.isbn}")