"""Tests for spinachlang used as a Python library.

Verifies:
  - The public API surface exposed by __init__.py
  - to_tket()   → pytket.Circuit          (always, no optional deps)
  - to_cirq()   → cirq.Circuit            (skipped if pytket-cirq absent)
  - to_braket() → braket.circuits.Circuit (skipped if pytket-braket absent)
  - to_pyquil() → pyquil.Program          (skipped if pytket-pyquil absent)
  - to_qiskit() → qiskit.QuantumCircuit   (skipped if pytket-qiskit absent)
  - Missing optional packages raise ImportError with a helpful install hint
  - Top-level convenience functions are properly re-exported
"""

import importlib.util
import sys
import unittest
import unittest.mock as mock

from pytket import Circuit as TketCircuit
from pytket.circuit import OpType

import spinachlang
from spinachlang import (
    Spinach,
    compile_code,
    create_tket_circuit,
    to_tket_circuit,
    to_cirq_circuit,
    to_braket_circuit,
    to_pyquil_program,
    to_qiskit_circuit,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BELL = """
q0 : q 0
q1 : q 1
q0 -> H
q0 -> CX(q1)
* -> M
"""

_SIMPLE = """
tom : q 0
tom -> H
"""


def _installed(package: str) -> bool:
    """Return True only if *package* can actually be imported without error.

    find_spec() is not enough — a package can have a spec but still fail to
    import (e.g. pytket-qiskit with a broken qiskit_ibm_runtime dependency).
    """
    try:
        importlib.import_module(package)
        return True
    except Exception:  # ImportError, AttributeError, etc.
        return False


# ---------------------------------------------------------------------------
# 1. Public API surface
# ---------------------------------------------------------------------------

class TestPublicAPI(unittest.TestCase):
    """Everything in __all__ must be importable from the top-level package."""

    def test_all_exports_present(self):
        for name in spinachlang.__all__:
            self.assertTrue(
                hasattr(spinachlang, name),
                f"spinachlang.__all__ lists {name!r} but the attribute is missing",
            )

    def test_spinach_class_importable(self):
        from spinachlang import Spinach as S  # noqa: F401
        self.assertIsNotNone(S)

    def test_all_convenience_functions_callable(self):
        for fn in (
            compile_code,
            create_tket_circuit,
            to_tket_circuit,
            to_cirq_circuit,
            to_braket_circuit,
            to_pyquil_program,
            to_qiskit_circuit,
        ):
            self.assertTrue(callable(fn), f"{fn!r} is not callable")

    def test_to_methods_exist_on_spinach_class(self):
        for name in ("to_tket", "to_cirq", "to_braket", "to_pyquil", "to_qiskit"):
            self.assertTrue(
                hasattr(Spinach, name),
                f"Spinach.{name} is missing",
            )

    def test_convenience_functions_are_same_as_class_methods(self):
        self.assertIs(to_tket_circuit,   Spinach.to_tket)
        self.assertIs(to_cirq_circuit,   Spinach.to_cirq)
        self.assertIs(to_braket_circuit, Spinach.to_braket)
        self.assertIs(to_pyquil_program, Spinach.to_pyquil)
        self.assertIs(to_qiskit_circuit, Spinach.to_qiskit)


# ---------------------------------------------------------------------------
# 2. Core — to_tket (always available, no optional deps)
# ---------------------------------------------------------------------------

class TestToTket(unittest.TestCase):
    """to_tket / to_tket_circuit requires only pytket core."""

    def test_returns_tket_circuit(self):
        self.assertIsInstance(Spinach.to_tket(_BELL), TketCircuit)

    def test_convenience_alias(self):
        self.assertIsInstance(to_tket_circuit(_BELL), TketCircuit)

    def test_legacy_create_circuit_alias(self):
        """create_tket_circuit is kept for back-compat."""
        self.assertIsInstance(create_tket_circuit(_BELL), TketCircuit)

    def test_bell_has_two_qubits(self):
        self.assertEqual(len(Spinach.to_tket(_BELL).qubits), 2)

    def test_bell_op_types(self):
        op_types = {cmd.op.type for cmd in Spinach.to_tket(_BELL).get_commands()}
        self.assertIn(OpType.H,       op_types)
        self.assertIn(OpType.CX,      op_types)
        self.assertIn(OpType.Measure, op_types)

    def test_single_qubit_circuit(self):
        c = Spinach.to_tket(_SIMPLE)
        self.assertIsInstance(c, TketCircuit)
        self.assertEqual(len(c.qubits), 1)

    def test_agrees_with_create_circuit(self):
        c1 = Spinach.to_tket(_BELL)
        c2 = Spinach.create_circuit(_BELL)
        self.assertEqual(
            len(c1.get_commands()),
            len(c2.get_commands()),
        )


# ---------------------------------------------------------------------------
# 3. Optional — to_cirq
# ---------------------------------------------------------------------------

@unittest.skipUnless(_installed("pytket.extensions.cirq"), "pytket-cirq not installed")
class TestToCirq(unittest.TestCase):

    def test_returns_cirq_circuit(self):
        import cirq
        self.assertIsInstance(Spinach.to_cirq(_BELL), cirq.Circuit)

    def test_convenience_alias(self):
        import cirq
        self.assertIsInstance(to_cirq_circuit(_BELL), cirq.Circuit)

    def test_simple_circuit_simulatable(self):
        import cirq
        result = cirq.Simulator().simulate(Spinach.to_cirq(_SIMPLE))
        self.assertIsNotNone(result.final_state_vector)

    def test_bell_has_operations(self):
        import cirq
        circuit = Spinach.to_cirq(_BELL)
        self.assertGreater(len(list(circuit.all_operations())), 0)


# ---------------------------------------------------------------------------
# 4. Optional — to_braket
# ---------------------------------------------------------------------------

@unittest.skipUnless(_installed("pytket.extensions.braket"), "pytket-braket not installed")
class TestToBraket(unittest.TestCase):

    def test_returns_braket_circuit(self):
        from braket.circuits import Circuit as BraketCircuit
        self.assertIsInstance(Spinach.to_braket(_BELL), BraketCircuit)

    def test_convenience_alias(self):
        from braket.circuits import Circuit as BraketCircuit
        self.assertIsInstance(to_braket_circuit(_BELL), BraketCircuit)

    def test_bell_has_instructions(self):
        self.assertGreater(len(Spinach.to_braket(_BELL).instructions), 0)

    def test_bell_qubit_count(self):
        self.assertEqual(Spinach.to_braket(_BELL).qubit_count, 2)

    def test_simple_circuit_local_simulator(self):
        """Run a statevector simulation via Braket LocalSimulator."""
        from braket.devices import LocalSimulator
        from braket.circuits import Circuit as BraketCircuit, Gate
        full = Spinach.to_braket(_SIMPLE)
        # Build a measurement-free copy for statevector sim
        sv = BraketCircuit()
        for instr in full.instructions:
            if isinstance(instr.operator, Gate):
                sv.add_instruction(instr)
        sv.state_vector()
        result = LocalSimulator().run(sv, shots=0).result()
        self.assertIsNotNone(result)


# ---------------------------------------------------------------------------
# 5. Optional — to_pyquil
# ---------------------------------------------------------------------------

@unittest.skipUnless(_installed("pytket.extensions.pyquil"), "pytket-pyquil not installed")
class TestToPyquil(unittest.TestCase):

    def test_returns_pyquil_program(self):
        from pyquil import Program
        self.assertIsInstance(Spinach.to_pyquil(_BELL), Program)

    def test_convenience_alias(self):
        from pyquil import Program
        self.assertIsInstance(to_pyquil_program(_BELL), Program)

    def test_program_has_instructions(self):
        self.assertGreater(len(Spinach.to_pyquil(_BELL).instructions), 0)


# ---------------------------------------------------------------------------
# 6. Optional — to_qiskit
# ---------------------------------------------------------------------------

@unittest.skipUnless(_installed("pytket.extensions.qiskit"), "pytket-qiskit not installed")
class TestToQiskit(unittest.TestCase):

    def test_returns_qiskit_circuit(self):
        from qiskit import QuantumCircuit
        self.assertIsInstance(Spinach.to_qiskit(_BELL), QuantumCircuit)

    def test_convenience_alias(self):
        from qiskit import QuantumCircuit
        self.assertIsInstance(to_qiskit_circuit(_BELL), QuantumCircuit)

    def test_bell_num_qubits(self):
        self.assertEqual(Spinach.to_qiskit(_BELL).num_qubits, 2)


# ---------------------------------------------------------------------------
# 7. ImportError quality — missing package → clear install hint
# ---------------------------------------------------------------------------

class TestImportErrorMessages(unittest.TestCase):
    """Each to_*() method must raise ImportError mentioning 'spinachlang[backends]'
    when its optional extension package is not available."""

    _EXT_MAP = {
        "to_cirq":   "pytket.extensions.cirq",
        "to_braket": "pytket.extensions.braket",
        "to_pyquil": "pytket.extensions.pyquil",
        "to_qiskit": "pytket.extensions.qiskit",
    }

    def _assert_helpful_error(self, method: str) -> None:
        ext = self._EXT_MAP[method]
        with mock.patch.dict(sys.modules, {ext: None}):
            with self.assertRaises(ImportError) as ctx:
                getattr(Spinach, method)(_SIMPLE)
        self.assertIn(
            "spinachlang[backends]",
            str(ctx.exception),
            f"Spinach.{method} ImportError should mention 'spinachlang[backends]'",
        )

    def test_cirq_hint(self):
        self._assert_helpful_error("to_cirq")

    def test_braket_hint(self):
        self._assert_helpful_error("to_braket")

    def test_pyquil_hint(self):
        self._assert_helpful_error("to_pyquil")

    def test_qiskit_hint(self):
        self._assert_helpful_error("to_qiskit")


if __name__ == "__main__":
    unittest.main()


