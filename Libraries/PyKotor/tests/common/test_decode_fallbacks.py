from __future__ import annotations

import pathlib
import sys
import unittest

from contextlib import suppress
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

    import charset_normalizer

THIS_SCRIPT_PATH = pathlib.Path(__file__).resolve()


def _repo_root(start: pathlib.Path) -> pathlib.Path:
    for ancestor in (start, *start.parents):
        if (ancestor / "Libraries" / "PyKotor" / "src" / "pykotor").is_dir():
            return ancestor
    return start.parents[4]


_REPO_ROOT = _repo_root(THIS_SCRIPT_PATH)
PYKOTOR_PATH = _REPO_ROOT / "Libraries" / "PyKotor" / "src"
UTILITY_PATH = _REPO_ROOT / "Libraries" / "PyKotor" / "src" / "utility"


def add_sys_path(p: pathlib.Path):
    working_dir = str(p)
    if working_dir not in sys.path:
        sys.path.append(working_dir)


if PYKOTOR_PATH.joinpath("pykotor").exists():
    add_sys_path(PYKOTOR_PATH)
if UTILITY_PATH.joinpath("utility").exists():
    add_sys_path(UTILITY_PATH)

from pykotor.common.language import Language  # noqa: E402
from pykotor.tools.encoding import decode_bytes_with_fallbacks  # noqa: E402

charset_normalizer: None | ModuleType
try:
    import charset_normalizer
except ImportError:
    charset_normalizer = None


def _decoding_alternatives(byte_content: bytes, errors: str) -> set[str]:
    """Cross-platform expected outputs: utf-8/latin-1 plus each charset_normalizer candidate."""
    alts: set[str] = set()
    with suppress(UnicodeDecodeError):
        alts.add(byte_content.decode("utf-8", errors=errors))
    with suppress(UnicodeDecodeError):
        alts.add(byte_content.decode("latin-1", errors=errors))
    if charset_normalizer is None:
        return alts
    for m in charset_normalizer.from_bytes(byte_content):
        try:
            alts.add(byte_content.decode(m.encoding, errors=errors))
        except (LookupError, UnicodeDecodeError):
            continue
    return alts


class TestDecodeBytes(unittest.TestCase):
    def test_basic(self):
        byte_str = b"hello world"
        result = decode_bytes_with_fallbacks(byte_str)
        assert result == "hello world"

    def test_non_ascii(self):
        byte_str = b"h\xc3\xa9llo w\xc3\xb6rld"
        result = decode_bytes_with_fallbacks(byte_str)
        assert result == "héllo wörld"

    def test_unknown_encoding(self):
        byte_str = b"\x80\x81\x82"
        with self.assertRaises(UnicodeDecodeError):
            byte_str.decode()
        result = byte_str.decode(errors="replace")
        assert result == "���"
        result = decode_bytes_with_fallbacks(byte_str, errors="replace")
        assert result in _decoding_alternatives(byte_str, "replace")

    def test_bom(self):
        byte_str = b"\xef\xbb\xbfhello world"
        result = byte_str.decode("utf-8-sig")
        assert result == "hello world"
        result = decode_bytes_with_fallbacks(byte_str)
        assert result == "hello world"

    def test_errors_replace(self):
        byte_str = b"h\xc3\xa9llo"
        # self.assertEqual(byte_str.decode(errors="replace"), "h?llo")
        assert byte_str.decode(errors="replace") == "héllo"

        result = decode_bytes_with_fallbacks(byte_str, errors="replace")
        assert result == "héllo"

    def test_known_encoding(self):
        byte_content = b"Hello, World!"
        errors = "strict"
        encoding = "utf-8"
        lang = None
        only_8bit_encodings = False
        expected_result = "Hello, World!"

        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result == expected_result

    def test_language_provided(self):
        byte_content = b"Bonjour le monde!"
        errors = "strict"
        encoding = None
        lang = Language.FRENCH
        only_8bit_encodings = False
        expected_result = "Bonjour le monde!"

        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result == expected_result

    def test_language_detect(self):
        byte_content = b"Bonjour le monde!"
        errors = "strict"
        encoding = None
        lang = None
        only_8bit_encodings = False
        expected_result = "Bonjour le monde!"

        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result == expected_result

    def test_invalid_bytes_for_encoding(self):
        byte_content = b"\xff\xfe\x00"
        errors = "replace"
        encoding = "utf-8"
        lang = None
        only_8bit_encodings = False
        expected_result = "\ufffd\ufffd"
        result = byte_content.decode(encoding, errors)
        assert result == "��\x00"

        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result in {"��\x00", "ÿþ\x00"}

    @unittest.skip("skipped - not ready for full test execution")
    def test_fallback_to_detected_encoding(self):
        byte_content = b"\xc2\xa1Hola!"
        errors = "strict"
        encoding = None
        lang = None
        only_8bit_encodings = False
        expected_result = "¡Hola!"
        exp = "癒Hola!"
        exp2 = "Â¡Hola!"

        result = byte_content.decode(errors=errors)
        assert result == expected_result
        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result == (exp2 if charset_normalizer is None else exp)

    def test_8bit_encoding_only(self):
        byte_content = b"\xe4\xf6\xfc"
        errors = "strict"
        encoding = None
        lang = None
        only_8bit_encodings = True
        expected_result = "���"
        exp = "U6Ü"
        exp2 = "дць"

        result = byte_content.decode(errors="replace")
        assert result == expected_result
        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result == (exp2 if charset_normalizer is None else exp)

    def test_with_BOM_included(self):
        byte_content = b"\xef\xbb\xbfTest"
        errors = "strict"
        encoding = None
        lang = None
        only_8bit_encodings = False
        expected_result = "Test"

        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result == expected_result

    def test_undetectable_encoding_replace_errors(self):
        byte_content = b"\x80\x81\x82"
        errors = "replace"
        encoding = None
        lang = None
        only_8bit_encodings = False
        expected_result = "\ufffd\ufffd\ufffd"

        result = byte_content.decode(errors=errors)
        assert result == expected_result
        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result in _decoding_alternatives(byte_content, errors)

    def test_strict_error_handling_decoding_failure(self):
        byte_content = b"\x80\x81\x82"
        errors = "strict"
        encoding = "ascii"
        lang = None
        only_8bit_encodings = False
        with self.assertRaises(UnicodeDecodeError):
            byte_content.decode(encoding, errors=errors)
        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result in _decoding_alternatives(byte_content, errors)

    def test_no_valid_encoding_found_strict_errors(self):
        byte_content = b"\x80\x81\x82"
        errors = "strict"
        encoding = None
        lang = None
        only_8bit_encodings = False
        with self.assertRaises(UnicodeDecodeError):
            byte_content.decode(errors=errors)
        result = decode_bytes_with_fallbacks(
            byte_content, errors, encoding, lang, only_8bit_encodings
        )
        assert result in _decoding_alternatives(byte_content, errors)
