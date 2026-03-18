"""Top-level package for SpinachLang.

Provides Spinach class and helper functions for circuit compilation and TKET integration.

String output (for files / CLI)
--------------------------------
compile_code(code, language)  →  str

Native object output (for simulation / library use)
-----------------------------------------------------
to_tket_circuit(code)    →  pytket.Circuit            (no extra install)
to_cirq_circuit(code)    →  cirq.Circuit              (needs pytket-cirq)
to_braket_circuit(code)  →  braket.circuits.Circuit   (needs pytket-braket)
to_pyquil_program(code)  →  pyquil.Program            (needs pytket-pyquil)
to_qiskit_circuit(code)  →  qiskit.QuantumCircuit     (needs pytket-qiskit)

Install optional backends: pip install 'spinachlang[backends]'
"""

from .spinach import Spinach

# ── legacy / string-output aliases ────────────────────────────────────────
compile_code        = Spinach.compile
create_tket_circuit = Spinach.create_circuit   # kept for back-compat

# ── native object aliases ──────────────────────────────────────────────────
to_tket_circuit   = Spinach.to_tket
to_cirq_circuit   = Spinach.to_cirq
to_braket_circuit = Spinach.to_braket
to_pyquil_program = Spinach.to_pyquil
to_qiskit_circuit = Spinach.to_qiskit

__all__ = [
    "Spinach",
    # string output
    "compile_code",
    "create_tket_circuit",
    # native object output
    "to_tket_circuit",
    "to_cirq_circuit",
    "to_braket_circuit",
    "to_pyquil_program",
    "to_qiskit_circuit",
]
