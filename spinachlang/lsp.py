"""SpinachLang Language Server Protocol (LSP) server.

Provides real-time diagnostics, hover documentation, and completion
for .sph source files via the Language Server Protocol.

Protocol layer: pygls 2.x with lsprotocol
Transport    : stdio (default) or TCP
"""

from __future__ import annotations

import logging
from typing import Optional

from lark import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken
from lsprotocol import types
from pygls.lsp.server import LanguageServer

from .parser import Parser

# ---------------------------------------------------------------------------
# Server identity
# ---------------------------------------------------------------------------
SERVER_NAME = "spinachlang-lsp"
SERVER_VERSION = "0.2.3"

logger = logging.getLogger(SERVER_NAME)

# ---------------------------------------------------------------------------
# Quantum gate catalogue
# Each entry: gate_name -> (short_signature, markdown_description)
# ---------------------------------------------------------------------------
_GATES: dict[str, tuple[str, str]] = {
    "H":       ("H qubit",          "**Hadamard** — creates superposition: |0⟩ → |+⟩, |1⟩ → |−⟩"),
    "X":       ("X qubit",          "**Pauli-X** (NOT) — bit-flip: |0⟩ ↔ |1⟩"),
    "Y":       ("Y qubit",          "**Pauli-Y** — combined bit and phase flip"),
    "Z":       ("Z qubit",          "**Pauli-Z** — phase flip: |1⟩ → −|1⟩"),
    "S":       ("S qubit",          "**S gate** — phase rotation by π/2 around Z"),
    "T":       ("T qubit",          "**T gate** — phase rotation by π/4 around Z"),
    "SDG":     ("SDG qubit",        "**S† gate** — adjoint S, phase rotation by −π/2"),
    "TDG":     ("TDG qubit",        "**T† gate** — adjoint T, phase rotation by −π/4"),
    "SX":      ("SX qubit",         "**√X gate** — square root of X"),
    "SXDG":    ("SXDG qubit",       "**√X† gate** — adjoint of √X"),
    "CX":      ("CX control target","**CNOT** — flips target when control is |1⟩"),
    "CY":      ("CY control target","**Controlled-Y** — applies Y when control is |1⟩"),
    "CZ":      ("CZ control target","**Controlled-Z** — phase flip when both qubits are |1⟩"),
    "CH":      ("CH control target","**Controlled-H** — applies Hadamard when control is |1⟩"),
    "SWAP":    ("SWAP q0 q1",       "**SWAP** — exchanges the quantum states of two qubits"),
    "ISWAP":   ("ISWAP q0 q1",      "**iSWAP** — swaps two qubits with a phase"),
    "CCX":     ("CCX c0 c1 target", "**Toffoli** (CCNOT) — flips target when both controls are |1⟩"),
    "CCZ":     ("CCZ c0 c1 target", "**Controlled-Controlled-Z** — applies Z when both controls are |1⟩"),
    "CSWAP":   ("CSWAP c q0 q1",    "**Fredkin** (Controlled-SWAP) — swaps two qubits if control is |1⟩"),
    "RX":      ("RX(θ) qubit",      "**RX(θ)** — rotation around X-axis by angle θ (radians)"),
    "RY":      ("RY(θ) qubit",      "**RY(θ)** — rotation around Y-axis by angle θ (radians)"),
    "RZ":      ("RZ(θ) qubit",      "**RZ(θ)** — rotation around Z-axis by angle θ (radians)"),
    "MEASURE": ("MEASURE qubit",    "**Measure** — collapses qubit to a classical bit"),
    "RESET":   ("RESET qubit",      "**Reset** — resets qubit to the |0⟩ state"),
    "BARRIER": ("BARRIER ...",      "**Barrier** — prevents optimisation across this point in the circuit"),
}

# Sorted gate names for stable completion lists
_GATE_NAMES: list[str] = sorted(_GATES)

# ---------------------------------------------------------------------------
# LSP server instance
# ---------------------------------------------------------------------------
server = LanguageServer(
    name=SERVER_NAME,
    version=SERVER_VERSION,
    text_document_sync_kind=types.TextDocumentSyncKind.Full,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _diagnostics_for(source: str) -> list[types.Diagnostic]:
    """Parse *source* with the Spinach frontend and return LSP diagnostics.

    Parameters
    ----------
    source:
        Full text of the .sph document.

    Returns
    -------
    list[types.Diagnostic]
        Empty when the source is syntactically valid; one or more error
        diagnostics otherwise.
    """
    try:
        Parser.get_tree(source)
        return []
    except UnexpectedCharacters as exc:
        line = max(0, exc.line - 1)
        col = max(0, exc.column - 1)
        lines = source.splitlines()
        char = lines[line][col] if line < len(lines) and col < len(lines[line]) else ""
        msg = f"Unexpected character '{char}'"
        if exc.allowed:
            msg += f". Expected one of: {', '.join(sorted(exc.allowed))}"
        return [_make_diagnostic(msg, line, col, col + 1)]

    except UnexpectedToken as exc:
        line = max(0, exc.line - 1)
        col = max(0, exc.column - 1)
        token = exc.token
        token_str = str(token)
        msg = f"Unexpected token '{token_str}'"
        if exc.expected:
            msg += f". Expected one of: {', '.join(sorted(exc.expected))}"

        # Prefer token position metadata to compute the diagnostic range.
        if hasattr(token, "end_column") and getattr(token, "end_column") is not None:
            # Lark columns are 1-based; convert to 0-based exclusive end index.
            end_col = max(0, token.end_column - 1)
        else:
            # Fallback: use the length of the token's raw value if available,
            # otherwise the string representation.
            token_text = getattr(token, "value", token_str)
            end_col = col + len(token_text)

        return [_make_diagnostic(msg, line, col, end_col)]

    except UnexpectedEOF as exc:
        lines = source.splitlines()
        last_line = max(0, len(lines) - 1)
        last_col = len(lines[last_line]) if lines else 0
        msg = "Unexpected end of file"
        if exc.expected:
            msg += f". Expected one of: {', '.join(sorted(exc.expected))}"
        return [_make_diagnostic(msg, last_line, last_col, last_col)]

    except Exception:  # pylint: disable=broad-except
        logger.exception("Unexpected internal error during parsing")
        return [_make_diagnostic("Internal parser error; see server logs for details.", 0, 0, 0)]


def _make_diagnostic(
    message: str,
    start_line: int,
    start_char: int,
    end_char: int,
) -> types.Diagnostic:
    """Build a single LSP error Diagnostic."""
    return types.Diagnostic(
        range=types.Range(
            start=types.Position(line=start_line, character=start_char),
            end=types.Position(line=start_line, character=end_char),
        ),
        message=message,
        severity=types.DiagnosticSeverity.Error,
        source=SERVER_NAME,
    )


def _publish(ls: LanguageServer, uri: str, source: str) -> None:
    """Parse *source* and push diagnostics for *uri* to the client."""
    diagnostics = _diagnostics_for(source)
    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
    )


# ---------------------------------------------------------------------------
# Lifecycle — document synchronisation
# ---------------------------------------------------------------------------

@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams) -> None:
    """Validate a .sph document as soon as it is opened."""
    _publish(ls, params.text_document.uri, params.text_document.text)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams) -> None:
    """Re-validate on every incremental or full content change."""
    # With TextDocumentSyncKind.Full the client always sends the entire text.
    source = params.content_changes[-1].text
    _publish(ls, params.text_document.uri, source)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    """Re-validate when the document is saved."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    _publish(ls, params.text_document.uri, doc.source)


@server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: LanguageServer, params: types.DidCloseTextDocumentParams) -> None:
    """Clear diagnostics when a document is closed."""
    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(uri=params.text_document.uri, diagnostics=[])
    )


# ---------------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------------

@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(trigger_characters=[" ", "|", ":"]),
)
def completions(
    ls: LanguageServer,  # noqa: ARG001
    params: types.CompletionParams,  # noqa: ARG001
) -> types.CompletionList:
    """Return completion items for all built-in quantum gates.

    Gate names are always UPPER_CASE in SpinachLang grammar (UPPER_NAME
    terminal), so every item is inserted as uppercase.
    """
    items = [
        types.CompletionItem(
            label=name,
            kind=types.CompletionItemKind.Function,
            detail=_GATES[name][0],
            documentation=types.MarkupContent(
                kind=types.MarkupKind.Markdown,
                value=_GATES[name][1],
            ),
            insert_text=name,
        )
        for name in _GATE_NAMES
    ]
    return types.CompletionList(is_incomplete=False, items=items)


# ---------------------------------------------------------------------------
# Hover
# ---------------------------------------------------------------------------

@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(
    ls: LanguageServer,
    params: types.HoverParams,
) -> Optional[types.Hover]:
    """Return markdown hover documentation for the gate under the cursor.

    Recognises both the exact case used in the source and the uppercase
    canonical form (e.g. ``cx`` and ``CX`` both resolve to the CX entry).
    """
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    pos = params.position

    if pos.line >= len(lines):
        return None

    line_text = lines[pos.line]
    col = pos.character

    # Expand word boundary around the cursor position
    start = col
    while start > 0 and (line_text[start - 1].isalnum() or line_text[start - 1] == "_"):
        start -= 1
    end = col
    while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == "_"):
        end += 1

    word = line_text[start:end]
    if not word:
        return None

    entry = _GATES.get(word.upper())
    if entry is None:
        return None

    sig, desc = entry
    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value=f"```spinach\n{sig}\n```\n\n{desc}",
        ),
        range=types.Range(
            start=types.Position(line=pos.line, character=start),
            end=types.Position(line=pos.line, character=end),
        ),
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def start_lsp_server() -> None:
    """Start the SpinachLang LSP server on stdio.

    This is the function called by the ``spinachlang-lsp`` console script.
    Editors connect to it via the standard LSP stdio transport.
    """
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
    logger.info("Starting %s v%s", SERVER_NAME, SERVER_VERSION)
    server.start_io()

