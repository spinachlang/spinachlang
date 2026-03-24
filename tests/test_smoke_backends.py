"""Smoke tests for all Spinach.compile() output backends.

Each test verifies that a complete source → string round-trip succeeds and
returns a non-empty string.  Optional backends (cirq, quil, braket, qir) are
skipped automatically when their extension package is not installed so that
the test suite passes in minimal environments.
"""

import importlib
import unittest

from spinachlang import Spinach

# ---------------------------------------------------------------------------
# Shared source snippets
# ---------------------------------------------------------------------------

_BELL = """
q0 : q 0
q1 : q 1
q0 -> H
q0 -> CX(q1)
* -> M
"""

# QIR requires explicit bit declarations and per-qubit measurements
_BELL_WITH_BITS = """
q0 : q 0
q1 : q 1
b0 : b 0
b1 : b 1
q0 -> H
q0 -> CX(q1)
q0 -> M(b0)
q1 -> M(b1)
"""


def _installed(package: str) -> bool:
    """Return True only if *package* can be imported without error."""
    try:
        importlib.import_module(package)
        return True
    except Exception:  # ImportError, AttributeError, broken transitive dep …
        return False


# ---------------------------------------------------------------------------
# Always-available backends (no optional deps beyond pytket core)
# ---------------------------------------------------------------------------

class TestSmokeQasm(unittest.TestCase):
    """Spinach.compile(code, 'qasm') — always available."""

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL, "qasm")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_contains_qasm_header(self):
        result = Spinach.compile(_BELL, "qasm")
        self.assertIn("OPENQASM", result)


class TestSmokeJson(unittest.TestCase):
    """Spinach.compile(code, 'json') — always available."""

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL, "json")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_is_valid_json(self):
        import json
        result = Spinach.compile(_BELL, "json")
        parsed = json.loads(result)
        self.assertIsInstance(parsed, dict)


class TestSmokeLatex(unittest.TestCase):
    """Spinach.compile(code, 'latex') — always available."""

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL, "latex")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_contains_latex_preamble(self):
        result = Spinach.compile(_BELL, "latex")
        self.assertIn("\\", result)


# ---------------------------------------------------------------------------
# Optional backends — skipped when the extension package is absent
# ---------------------------------------------------------------------------

@unittest.skipUnless(_installed("pytket.extensions.cirq"), "pytket-cirq not installed")
class TestSmokeCirq(unittest.TestCase):
    """Spinach.compile(code, 'cirq') — requires pytket-cirq."""

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL, "cirq")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


@unittest.skipUnless(_installed("pytket.extensions.pyquil"), "pytket-pyquil not installed")
class TestSmokeQuil(unittest.TestCase):
    """Spinach.compile(code, 'quil') — requires pytket-pyquil (Python <=3.12)."""

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL, "quil")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


@unittest.skipUnless(_installed("pytket.extensions.braket"), "pytket-braket not installed")
class TestSmokeBraket(unittest.TestCase):
    """Spinach.compile(code, 'braket') — requires pytket-braket."""

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL, "braket")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


@unittest.skipUnless(_installed("pytket.extensions.qir"), "pytket-qir not installed")
class TestSmokeQir(unittest.TestCase):
    """Spinach.compile(code, 'qir') — requires pytket-qir.

    QIR requires explicit classical bit declarations and per-qubit measurements
    (wildcard ``* -> M`` is not sufficient).
    """

    def test_returns_nonempty_string(self):
        result = Spinach.compile(_BELL_WITH_BITS, "qir")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


# ---------------------------------------------------------------------------
# Unknown language raises ValueError
# ---------------------------------------------------------------------------

class TestSmokeUnknownLanguage(unittest.TestCase):
    """Requesting an unsupported target must raise ValueError."""

    def test_unknown_language_raises(self):
        with self.assertRaises(ValueError):
            Spinach.compile(_BELL, "cobol")


if __name__ == "__main__":
    unittest.main()

