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
# 1. Enter the dev shell (sets LD_LIBRARY_PATH for pytket)
nix-shell

# 2. Create and activate a virtual environment
uv venv
source .venv/bin/activate

# 3. Install the package
uv pip install .

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
