# Spinach lang
![logo for Spinach](spinach.png "Spinach")
Spinach is a quantum programming language.
Its goal is to provide a dedicated language that can simulate and compile code for execution on quantum computers.

[documentation](https://spinachlang.github.io/spinachsite/)


[source](https://github.com/spinachlang/spinachlang)


[examples](https://github.com/spinachlang/spinachlang-algorithms)

---

## Installation

### Standard (Linux / macOS / Windows)

Requires **Python 3.10+** and [`uv`](https://docs.astral.sh/uv/).

```bash
# 1. Create and activate a virtual environment
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install the package
uv pip install spinachlang

# 3. Verify
spinachlang --help
```

To also install optional quantum backend extensions (Cirq, Quil, Qiskit, etc.):

```bash
uv pip install "spinachlang[backends]"
```

### NixOS

PyTKET requires `libstdc++.so.6` which is not in the default library search path on NixOS.
`shell.nix` sets `LD_LIBRARY_PATH` to expose it automatically.

On NixOS 24.05+, `NIX_PATH` contains a `flake:nixpkgs` entry, which causes `nix-shell`
to fail with `"experimental Nix feature 'flakes' is disabled"` unless flakes are enabled.
Enable them once with:

```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

Then install normally:

```bash
# 1. Enter the dev shell (sets LD_LIBRARY_PATH, auto-creates .venv)
nix-shell

# 2. Activate the virtual environment (created automatically by nix-shell)
source .venv/bin/activate

# 3. Install the package and all development dependencies
uv pip install '.[lsp,dev]'

# 4. Verify
spinachlang --help
```

Or as a one-liner:

```bash
nix-shell --run 'uv pip install . && .venv/bin/spinachlang --help'
```

> **Note:** always run `spinachlang` from inside `nix-shell` (or with the
> `LD_LIBRARY_PATH` it sets) so that pytket's C++ extensions can find `libstdc++.so.6`.

---

## Usage

```bash
spinachlang -l qasm path/to/program.sph          # compile to OpenQASM
spinachlang -l cirq  path/to/program.sph          # compile to Cirq (Python)
spinachlang -l quil  path/to/program.sph          # compile to Quil
spinachlang -l json  path/to/program.sph          # compile to TKET JSON
spinachlang -l qasm  path/to/program.sph -o out.qasm  # specify output file
cat program.sph | spinachlang -l qasm -           # read from stdin, write to stdout
```

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/spinachlang/spinachlang.git
cd spinachlang

  # NixOS: enter the dev shell first
  nix-shell          # sets LD_LIBRARY_PATH for pytket

# Install with dev dependencies
uv pip install ".[dev]"
```

---

## Testing

```bash
# Run all tests
.venv/bin/pytest tests/

# Run a specific test module
.venv/bin/pytest tests/test_compiler.py

# Run with verbose output
.venv/bin/pytest tests/ -v

# Run with coverage
.venv/bin/pytest tests/ --cov=spinachlang
```

On **NixOS**, run tests from inside `nix-shell`:

```bash
nix-shell --run '.venv/bin/pytest tests/ -v'
```

---

## Gate Reference

All angles are expressed in **half-turns** (multiples of π).  
`RX(0.5)` = rotation by π/2 rad.  Decimal literals are supported: `RX(0.5)`, `TK1(0.25, 0.5, 0.75)`, etc.

### Single-qubit gates

| Spinach name | PyTKET gate | Parameters | Notes |
|---|---|---|---|
| `H` | `H` | — | Hadamard |
| `X` / `N` | `X` | — | Pauli X / NOT |
| `Y` | `Y` | — | Pauli Y |
| `Z` | `Z` | — | Pauli Z |
| `S` | `S` | — | S gate |
| `ST` | `Sdg` | — | S† |
| `T` | `T` | — | T gate |
| `TT` | `Tdg` | — | T† |
| `SX` | `SX` | — | √X |
| `SXDG` | `SXdg` | — | √X† |
| `V` | `V` | — | V gate (≡ √X in TKET) |
| `VDG` | `Vdg` | — | V† |
| `RX(a)` | `Rx` | 1 angle | Rotation around X |
| `RY(a)` | `Ry` | 1 angle | Rotation around Y |
| `RZ(a)` | `Rz` | 1 angle | Rotation around Z |
| `U1(λ)` | `U1` | 1 angle | IBM diagonal gate |
| `U2(φ,λ)` | `U2` | 2 angles | IBM 2-angle gate |
| `U3(θ,φ,λ)` | `U3` | 3 angles | IBM full SU(2) |
| `TK1(α,β,γ)` | `TK1` | 3 angles | TKET Euler decomposition |
| `PX(exp,ph)` / `PHASEDX(exp,ph)` | `PhasedX` | 2 angles | X rotation around a phase-shifted axis |
| `RESET` / `R` | `Reset` | — | Reset to \|0⟩ |

### Two-qubit gates

Convention: `target -> GATE(…, ctrl_or_partner)` — the last positional arg is always the partner qubit (by integer index or name).

| Spinach name | PyTKET gate | Parameters | Notes |
|---|---|---|---|
| `CX(ctrl)` / `CNOT(ctrl)` | `CX` | ctrl | Controlled-X |
| `FCX(ctrl)` / `FCNOT(ctrl)` | `CX` (flipped) | ctrl | CX with roles swapped |
| `CY(ctrl)` | `CY` | ctrl | Controlled-Y |
| `FCY(ctrl)` | `CY` (flipped) | ctrl | |
| `CZ(ctrl)` | `CZ` | ctrl | Controlled-Z |
| `FCZ(ctrl)` | `CZ` (flipped) | ctrl | |
| `CH(ctrl)` | `CH` | ctrl | Controlled-H |
| `FCH(ctrl)` | `CH` (flipped) | ctrl | |
| `CU1(a,ctrl)` | `CU1` | 1 angle + ctrl | Controlled-U1 |
| `CRX(a,ctrl)` | `CRx` | 1 angle + ctrl | Controlled-Rx |
| `CRY(a,ctrl)` | `CRy` | 1 angle + ctrl | Controlled-Ry |
| `CRZ(a,ctrl)` | `CRz` | 1 angle + ctrl | Controlled-Rz |
| `SWAP(other)` | `SWAP` | other | SWAP |
| `ECR(ctrl)` | `ECR` | ctrl | Echoed Cross-Resonance |
| `ISWAP(a,other)` | `ISWAP` | 1 angle + other | iSWAP with phase |
| `ISWAPMAX(other)` | `ISWAPMax` | other | Maximal iSWAP (≡ ISWAP(1)) |
| `ZZMAX(other)` | `ZZMax` | other | ZZMax (≡ ZZPhase(½)) |
| `ZZPH(a,other)` | `ZZPhase` | 1 angle + other | ZZ interaction |
| `XXPH(a,other)` | `XXPhase` | 1 angle + other | XX interaction |
| `YYPH(a,other)` | `YYPhase` | 1 angle + other | YY interaction |
| `FSIM(θ,φ,other)` | `FSim` | 2 angles + other | Fermionic Simulation |
| `TK2(a,b,c,other)` | `TK2` | 3 angles + other | TKET canonical 2-qubit |
| `PHISWAP(p,t,other)` | `PhasedISWAP` | 2 angles + other | Phased iSWAP |

### Three-qubit gates

| Spinach name | PyTKET gate | Parameters | Notes |
|---|---|---|---|
| `CCX(c1,c2)` / `TOFFOLI(c1,c2)` | `CCX` | 2 controls | Toffoli |
| `CSWAP(ctrl,other)` / `FREDKIN(ctrl,other)` | `CSWAP` | ctrl + other | Fredkin — swaps target↔other when ctrl=\|1⟩ |
| `XXP3(a,q1,q2)` | `XXPhase3` | 1 angle + 2 partners | Simultaneous XX on all pairs |

### Measurement & classical

| Spinach name | Effect | Notes |
|---|---|---|
| `M` / `MEASURE` | Measure to classical bit | `* -> M` measures all qubits |
| `BARRIER` | Synchronisation point | Cross-qubit, no-reorder fence |
| `SET(0\|1)` | Set bit to 0 or 1 | Classical bit target |
| `NOT` / `NOT(src)` | Classical NOT | In-place or with source |
| `AND(b0,b1)` | Classical AND | 2 bit args |
| `OR(b0,b1)` | Classical OR | 2 bit args |
| `XOR(b0,b1)` | Classical XOR | 2 bit args |
| `COPY(src)` | Copy bit | |

### Global phase & CircBox

```spinach
# Global phase: PHASE(angle) adds e^{i·angle·π} to the circuit scalar.
# The qubit target is syntactically required but ignored.
0 -> PHASE(0.5)

# CircBox: wrap a named instruction pipeline as a reusable black-box sub-circuit.
# The box has abstract qubits 0…n-1 mapping to the target list in order.
bell : H | CX(1)
q0 : q 0
q1 : q 1
[q0, q1] -> CIRCBOX(bell)
```

