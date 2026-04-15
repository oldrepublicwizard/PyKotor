from __future__ import annotations

import unittest

from typing import Any

from utility.common.misc_string.mutable_str import WrappedStr


class TestMutableStr(unittest.TestCase):
    def test_core_protocol(self):
        wrapped = WrappedStr("Test")

        self.assertEqual(wrapped._content, "Test")
        self.assertEqual(str(wrapped), "Test")
        self.assertEqual(repr(wrapped), "WrappedStr('Test')")
        self.assertTrue(issubclass(WrappedStr, str))
        self.assertEqual(hash(wrapped), hash("Test"))
        self.assertTrue(bool(wrapped))
        self.assertFalse(bool(WrappedStr("")))

    def test_comparison_operators_match_string_behavior(self):
        same = WrappedStr("Test")
        other = WrappedStr("Other")

        self.assertEqual(same, WrappedStr("Test"))
        self.assertEqual(same, "Test")
        self.assertNotEqual(same, "test")
        self.assertNotEqual(same, other)
        self.assertLess(WrappedStr("abc"), WrappedStr("def"))
        self.assertLessEqual(WrappedStr("abc"), "abc")
        self.assertGreater(WrappedStr("def"), WrappedStr("abc"))
        self.assertGreaterEqual(WrappedStr("def"), "def")

    def test_indexing_and_iteration_return_wrapped_values(self):
        wrapped = WrappedStr("test")

        self.assertEqual(wrapped[0], WrappedStr("t"))
        self.assertEqual(wrapped[1:3], WrappedStr("es"))
        self.assertEqual(list(iter(wrapped)), [WrappedStr("t"), WrappedStr("e"), WrappedStr("s"), WrappedStr("t")])
        self.assertEqual(list(reversed(wrapped)), [WrappedStr("t"), WrappedStr("s"), WrappedStr("e"), WrappedStr("t")])
        self.assertEqual(len(wrapped), 4)
        self.assertIn("e", wrapped)
        self.assertNotIn("E", wrapped)

    def test_binary_operators_preserve_wrapped_type(self):
        wrapped = WrappedStr("Test")

        self.assertEqual(wrapped + WrappedStr("ing"), WrappedStr("Testing"))
        self.assertEqual(wrapped + "ing", WrappedStr("Testing"))
        self.assertEqual(wrapped * 3, WrappedStr("TestTestTest"))
        self.assertEqual(WrappedStr("Hello, %s") % "World", WrappedStr("Hello, World"))

    def test_common_transformations_delegate_to_string_behavior(self):
        cases: list[tuple[str, WrappedStr, WrappedStr]] = [
            ("capitalize", WrappedStr("test").capitalize(), WrappedStr("Test")),
            ("casefold", WrappedStr("TeSt").casefold(), WrappedStr("test")),
            ("lower", WrappedStr("TEST").lower(), WrappedStr("test")),
            ("upper", WrappedStr("test").upper(), WrappedStr("TEST")),
            ("strip", WrappedStr("   test   ").strip(), WrappedStr("test")),
            ("replace", WrappedStr("test").replace("t", "x"), WrappedStr("xesx")),
            ("removeprefix", WrappedStr("TestPrefix").removeprefix("Test"), WrappedStr("Prefix")),
            ("removesuffix", WrappedStr("TestSuffix").removesuffix("Suffix"), WrappedStr("Test")),
            ("zfill", WrappedStr("42").zfill(5), WrappedStr("00042")),
        ]

        for label, actual, expected in cases:
            with self.subTest(method=label):
                self.assertEqual(actual, expected)

    def test_string_queries_match_expected_results(self):
        wrapped = WrappedStr("test test")

        self.assertEqual(wrapped.count("t"), 4)
        self.assertTrue(wrapped.endswith("st"))
        self.assertEqual(wrapped.find("e"), 1)
        self.assertEqual(wrapped.rfind("t"), 8)
        self.assertEqual(wrapped.index("e"), 1)
        self.assertEqual(wrapped.rindex("t"), 8)
        self.assertTrue(wrapped.startswith("te"))
        with self.assertRaises(ValueError):
            wrapped.index("E")

    def test_split_partition_and_join_preserve_wrapped_types(self):
        wrapped = WrappedStr("test test test")

        self.assertEqual(
            wrapped.partition("e"),
            (WrappedStr("t"), WrappedStr("e"), WrappedStr("st test test")),
        )
        self.assertEqual(
            wrapped.rpartition("t"),
            (WrappedStr("test test tes"), WrappedStr("t"), WrappedStr("")),
        )
        self.assertEqual(wrapped.split(), [WrappedStr("test"), WrappedStr("test"), WrappedStr("test")])
        self.assertEqual(wrapped.rsplit(), [WrappedStr("test"), WrappedStr("test"), WrappedStr("test")])
        self.assertEqual(WrappedStr(",").join(["a", "b", "c"]), WrappedStr("a,b,c"))

    def test_formatting_helpers_and_pickling_protocol(self):
        wrapped = WrappedStr("test")

        self.assertEqual(WrappedStr("Hello, {}").format("World"), WrappedStr("Hello, World"))
        self.assertEqual(
            WrappedStr("Hello, {name}").format_map({"name": "World"}),
            WrappedStr("Hello, World"),
        )
        self.assertEqual(format(wrapped, "<10"), "test      ")
        self.assertEqual(format(wrapped, ">10"), "      test")
        self.assertEqual(format(wrapped, "^10"), "   test   ")
        self.assertEqual(wrapped.__getstate__(), "test")
        self.assertEqual(wrapped.__getnewargs__(), ("test",))
        self.assertIsInstance(wrapped.__sizeof__(), int)

        reduced: tuple[Any, ...] = wrapped.__reduce__()
        reduced_ex: tuple[Any, ...] = wrapped.__reduce_ex__(2)
        self.assertEqual(reduced[0], WrappedStr)
        self.assertEqual(reduced[1], ("test",))
        self.assertEqual(reduced_ex[0], WrappedStr)
        self.assertEqual(reduced_ex[1], ("test",))

    def test_reflected_string_api_examples(self):
        wrapped = WrappedStr("Test123")

        self.assertTrue(wrapped.isalnum())
        self.assertFalse(WrappedStr("Test 123").isalnum())
        self.assertTrue(WrappedStr("Test Title").istitle())
        self.assertFalse(WrappedStr("Test title").istitle())
        self.assertEqual(WrappedStr("test\ntest\rtest").splitlines(), [WrappedStr("test"), WrappedStr("test"), WrappedStr("test")])
        self.assertEqual(WrappedStr("test").translate(str.maketrans("tes", "123")), WrappedStr("1231"))
        self.assertIn("lower", dir(wrapped))
        self.assertIn("upper", dir(wrapped))
        self.assertIn("_content", dir(wrapped))


if __name__ == "__main__":
    try:
        import pytest
    except ImportError:
        unittest.main()
    else:
        pytest.main(["-v", __file__])
