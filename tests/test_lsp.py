"""Tests for the SpinachLang LSP server.

These tests exercise the pure-Python helpers exposed by ``spinachlang.lsp``
without requiring the compiled pytket native extension: lightweight stubs are
installed into ``sys.modules`` before the package is imported so that the
pytket-dependent parts of the package load without error.
"""

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Stub pytket *only if it is not installed*, and do so *before* importing
# spinachlang so the backend / types modules can be imported without the
# compiled C extension being present. The LSP server only calls
# Parser.get_tree(), which depends only on lark.
# ---------------------------------------------------------------------------
try:
    # If pytket is installed, use the real package and avoid injecting
    # MagicMock stubs into sys.modules so other tests are not affected.
    import pytket  # type: ignore[unused-import]
except ImportError:
    # pytket is not available: install lightweight MagicMock stubs into
    # sys.modules so that spinachlang.lsp and its dependencies import cleanly.
    for _mod in (
        "pytket",
        "pytket._tket",
        "pytket._tket.architecture",
        "pytket.architecture",
        "pytket.circuit",
        "pytket.backends",
        "pytket.passes",
        "pytket.predicates",
        "pytket.extensions",
        "pytket.extensions.cirq",
        "pytket.extensions.pyquil",
        "pytket.extensions.qiskit",
        "pytket.extensions.pennylane",
        "pytket.extensions.braket",
        "pytket.extensions.projectq",
        "pytket.extensions.qir",
        "pytket.qasm",
        "pytket.qasm.qasm",
    ):
        sys.modules.setdefault(_mod, MagicMock())

    # Make `from pytket import Circuit, Qubit, Bit` resolve to MagicMock instances.
    _pytket_stub = sys.modules["pytket"]
    _pytket_stub.Circuit = MagicMock(name="Circuit")
    _pytket_stub.Qubit = MagicMock(name="Qubit")
    _pytket_stub.Bit = MagicMock(name="Bit")

    # Ensure `pytket.extensions` behaves as a real package so attribute access
    # like `pytket.extensions.cirq` resolves without AttributeError.
    _ext_stub = sys.modules["pytket.extensions"]
    _ext_stub.cirq = sys.modules["pytket.extensions.cirq"]
    _ext_stub.pyquil = sys.modules["pytket.extensions.pyquil"]

# ---------------------------------------------------------------------------

import pytest  # noqa: E402  (must come after sys.modules patching)

from spinachlang.lsp import (  # noqa: E402
    _GATE_NAMES,
    _GATES,
    _diagnostics_for,
    SERVER_NAME,
    SERVER_VERSION,
    server,
)
from lsprotocol import types  # noqa: E402


# ---------------------------------------------------------------------------
# _diagnostics_for — diagnostics helper
# ---------------------------------------------------------------------------

VALID_SOURCE = """\
q0 : q0
q1 : q1
bell : H | CX(q1)
q0 -> bell
"""

INVALID_SOURCE_BAD_CHAR = "q0 : q0\n@@@ garbage"
INVALID_SOURCE_EOF = "q0 : q"   # incomplete qubit declaration


class TestDiagnosticsFor:
    """Unit tests for _diagnostics_for()."""

    def test_valid_source_returns_empty(self):
        """Well-formed source must produce zero diagnostics."""
        diags = _diagnostics_for(VALID_SOURCE)
        assert diags == []

    def test_invalid_source_returns_error(self):
        """Bad syntax must produce at least one Error diagnostic."""
        diags = _diagnostics_for(INVALID_SOURCE_BAD_CHAR)
        assert len(diags) >= 1
        assert all(d.severity == types.DiagnosticSeverity.Error for d in diags)

    def test_diagnostic_has_source_tag(self):
        """Every diagnostic must carry the server name as its source."""
        diags = _diagnostics_for(INVALID_SOURCE_BAD_CHAR)
        assert all(d.source == SERVER_NAME for d in diags)

    def test_diagnostic_range_is_valid(self):
        """Diagnostic range must have non-negative line and character values."""
        diags = _diagnostics_for(INVALID_SOURCE_BAD_CHAR)
        for d in diags:
            assert d.range.start.line >= 0
            assert d.range.start.character >= 0
            assert d.range.end.line >= 0
            assert d.range.end.character >= 0

    def test_eof_error_is_caught(self):
        """Incomplete source must produce a diagnostic rather than crashing."""
        diags = _diagnostics_for(INVALID_SOURCE_EOF)
        assert len(diags) >= 1

    def test_empty_source_returns_error(self):
        """Empty source must produce a diagnostic (grammar requires ≥1 statement)."""
        diags = _diagnostics_for("")
        assert len(diags) >= 1

    def test_message_is_non_empty(self):
        """Every diagnostic must carry a human-readable message."""
        diags = _diagnostics_for(INVALID_SOURCE_BAD_CHAR)
        assert all(d.message for d in diags)


# ---------------------------------------------------------------------------
# Gate catalogue
# ---------------------------------------------------------------------------

class TestGateCatalogue:
    """Sanity checks for the gate catalogue used by completions and hover."""

    @pytest.mark.parametrize("name", ["H", "X", "Y", "Z", "CX", "RX", "RY", "RZ", "SWAP"])
    def test_common_gates_present(self, name: str):
        """Core quantum gates must appear in the catalogue."""
        assert name in _GATES

    def test_all_entries_have_sig_and_desc(self):
        """Every gate entry must have a non-empty signature and description."""
        for name, (sig, desc) in _GATES.items():
            assert sig, f"{name} has empty signature"
            assert desc, f"{name} has empty description"

    def test_gate_names_sorted(self):
        """_GATE_NAMES must be sorted for deterministic completion ordering."""
        assert _GATE_NAMES == sorted(_GATE_NAMES)


# ---------------------------------------------------------------------------
# Server identity
# ---------------------------------------------------------------------------

class TestServerIdentity:
    """Verify server metadata is correctly wired."""

    def test_server_name(self):
        assert SERVER_NAME == "spinachlang-lsp"

    def test_server_version_matches(self):
        assert SERVER_VERSION == server.version

    def test_server_name_matches(self):
        assert SERVER_NAME == server.name

