# AGENTS.md — SpinachLang Codebase Guide

## Architecture Overview

SpinachLang is a quantum programming language compiler with a strict 5-stage pipeline:

```
.sph source
  → Parser (Lark LALR, grammar.lark)          [spinachlang/parser.py]
  → Lark Tree
  → AstBuilder (Lark Transformer)              [spinachlang/ast_builder.py]
  → list[Pydantic AST nodes]                  [spinachlang/spinach_types.py]
  → Backend.compile_to_circuit()               [spinachlang/backend.py]
  → pytket.Circuit
  → format-specific string (QASM/JSON/Cirq/Quil)
```

The public entry point is `Spinach.compile(code, language)` in `spinach.py`. The `__init__.py` re-exports `compile_code` and `create_tket_circuit` as the Python API.

---

## Spinach Language Syntax Quick Reference

```spinach
# Declarations (lowercase names)
tom  : q 0          # qubit at register index 0 → Qubit("q", 0)
flag : b 0          # classical bit → Bit("c", 0)
grp  : [tom, alice] # list alias
bell : H | CX(1)    # named instruction (gate pipeline)

# Actions
tom -> H            # apply gate H to qubit "tom"
0 -> 3 X            # apply X gate 3 times to qubit index 0
* -> M              # apply to ALL qubits in circuit
[tom, alice] -> H   # apply to list
tom -> H | CX(1)    # gate pipeline
tom -> bell <-      # run named instruction in reverse

# Conditional
tom -> X if flag
tom -> X if flag else Z
```

**Naming rules (from `grammar.lark`):**
- User-defined names (`NAME`): lowercase start — `[a-z][a-zA-Z0-9_]*`
- Gate names (`UPPER_NAME`): uppercase start — `[A-Z][A-Z0-9]*`
- `F`-prefixed gates (`FCX`, `FCY`, `FCZ`, `FCH`) swap control/target vs. their standard counterparts

---

## Backend Gate Dispatch Pattern

New gates are added in two steps in `backend.py`:

1. **Write a handler** — `@staticmethod __handle_<gate>_gate(c, target, args, cond)` (single-target; wraps into multi-target via `_per_target`).
2. **Register in `__qubit_dispatch`** (or `__bit_dispatch` for classical ops) — a dict mapping the gate name string to the wrapped handler.

Group handlers (`MEASURE`/`BARRIER`) receive the full target list and must NOT be wrapped with `_per_target`.

The `cond` argument is `{"condition_bits": [bit], "condition_value": 0|1}` or `None`; always passed as `**cond` to PyTKET methods.

---

## PyTKET Register Conventions

| SpinachLang concept | PyTKET object              |
|---------------------|----------------------------|
| `q 0`               | `Qubit("q", 0)`            |
| `b 0`               | `Bit("c", 0)`              |
| Circuit default     | `Circuit()` (no named regs)|

Always use `Backend.DEFAULT_QUBIT_REGISTER = "q"` and `DEFAULT_BIT_REGISTER = "c"` constants; never hard-code `"q"` or `"c"` in new code.

---

## Developer Workflows

```bash
# Install for development
uv venv && source .venv/bin/activate
uv pip install .                        # core
uv pip install ".[backends]"            # optional: Cirq, Quil, Qiskit…

# Run the compiler
spinachlang -l qasm path/to/file.sph
cat prog.sph | spinachlang -l json -   # stdin → stdout

# Run tests
pytest                                  # all tests
pytest tests/test_compiler.py -v       # specific module

# Run LSP server (stdio, for editors)
spinachlang-lsp
spinachlang-lsp --tcp --port 2087      # TCP mode for debugging

# Build distribution
python -m build
twine check dist/*
```

**NixOS only**: always run inside `nix-shell` (sets `LD_LIBRARY_PATH` for PyTKET's C++ shared library `libstdc++.so.6`). See `shell.nix`.

---

## Key Patterns & Conventions

### Lark grammar cache
`_build_parser()` in `parser.py` is decorated with `@lru_cache(maxsize=1)` — the grammar file is read and compiled once per process. Do not call `Lark(...)` anywhere else.

### Pydantic models with PyTKET types
All AST node models in `spinach_types.py` use `class Config: arbitrary_types_allowed = True` because `Qubit` and `Bit` are C++ extension types Pydantic cannot introspect normally.

### Functional reduce over AST
`Backend.compile_to_circuit()` uses `functools.reduce` + `match/case` to fold AST nodes into a `(Circuit, index)` pair. `index` is a flat `dict[str, Qubit | Bit | GatePipeline | list]` built up as declarations are processed — it serves as the symbol table.

### Optional backend imports
`compile_to_cirq_python` and `compile_to_quil` import `pytket.extensions.*` inside the function body and raise `ImportError` with an install hint if missing. Follow this pattern for any new optional backend.

### ExitCode enum
CLI errors always call `sys.exit(ExitCode.<CODE>)` (defined in `exit_code.py`). Never use bare integer exit codes.

---

## Test Organization

| File | What it tests |
|------|---------------|
| `test_compiler.py` | `Backend.compile_to_circuit()` using manually constructed AST nodes |
| `test_ast_builder.py` | `AstBuilder` transformer rules |
| `test_spinach_front.py` | End-to-end: `.sph` source → circuit via `Spinach.create_circuit()` |
| `test_critical_features.py` | Conditional actions, list targets, repeat counts |
| `test_extended_gates.py` | FCX/FCY/CCX/SWAP/rotation gates |
| `test_high_features.py` | Named instructions, reverse pipelines, wildcard `*` |
| `test_lsp.py` | LSP diagnostics and completions |

Tests in `test_compiler.py` build AST nodes directly — useful for isolating backend logic without the parser. End-to-end tests prefer raw `.sph` strings via `Spinach.create_circuit()`.

---

## Key Files

| Path | Purpose |
|------|---------|
| `spinachlang/grammar.lark` | Authoritative Spinach grammar (LALR) |
| `spinachlang/spinach_types.py` | All AST node Pydantic models |
| `spinachlang/backend.py` | Gate dispatch tables + circuit builder |
| `spinachlang/spinach.py` | Thin façade wiring parser → AST → backend |
| `spinachlang-algorithms/*.sph` | Reference algorithm implementations |
| `pyproject.toml` | Pinned exact dependency versions (intentional) |

