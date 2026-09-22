"""Synthetic checks for the inert environment-input classifier."""

from __future__ import annotations

import unittest

from evaluation.downstream_benchmark.screening.audit_environment import (
    _decode_requirements,
    classify_setup_line,
)


class EnvironmentAuditTests(unittest.TestCase):
    def test_setup_lines_are_classified_without_execution(self) -> None:
        examples = {
            "pip3 install -r requirements.txt": "DEPENDENCY_INSTALL",
            "python setup.py build_ext --inplace": "PROJECT_INSTALL_OR_BUILD",
            "pip3 install -e .[test]": "PROJECT_INSTALL_OR_BUILD",
            "touch tests/__init__.py": "FILESYSTEM_PREPARATION",
            "export PYTHONPATH=/src": "ENVIRONMENT_CONFIGURATION",
            "pytest tests/test_x.py": "TEST_INVOCATION",
            "python setup.py test": "TEST_INVOCATION",
            "curl https://example.invalid": "NETWORK_OR_EXTERNAL_SERVICE",
            "do_something_unclear": "UNSUPPORTED_OR_AMBIGUOUS",
            "pip install pytest": "DEPENDENCY_INSTALL",
        }
        for line, expected in examples.items():
            with self.subTest(line=line):
                self.assertEqual(classify_setup_line(line), expected)

    def test_utf16_requirements_are_decoded_but_raw_bytes_remain_distinct(self) -> None:
        source = "attrs==19.3.0\n"
        decoded, encoding = _decode_requirements(source.encode("utf-16"))
        self.assertEqual((decoded, encoding), (source, "UTF-16_WITH_BOM"))
        self.assertNotEqual(source.encode("utf-16"), source.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
