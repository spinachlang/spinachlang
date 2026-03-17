"""Tests for the high-priority features:
  1. Classical bit operations  (NOT, SET, AND, OR, XOR, COPY)
  2. BARRIER
"""

import unittest

from pytket import Qubit, Bit
from pytket.circuit import OpType

from spinachlang.spinach import Spinach
from spinachlang.backend import Backend
from spinachlang.spinach_types import (
    BitDeclaration,
    QubitDeclaration,
    Action,
    GatePipeline,
    GateCall,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _circuit_from_source(code: str):
    return Spinach.create_circuit(code)


def _op_types(circuit):
    return [cmd.op.type for cmd in circuit.get_commands()]


# ---------------------------------------------------------------------------
# 1. Classical bit operations via AST
# ---------------------------------------------------------------------------

class TestBitOpsAST(unittest.TestCase):
    """Backend-level tests using hand-built ASTs (no parser needed)."""

    def _base(self, *extra_nodes):
        """Return AST with one qubit and two bits pre-declared."""
        return [
            QubitDeclaration(name="q0", qubit=Qubit("q", 0)),
            BitDeclaration(name="b0", bit=Bit("c", 0)),
            BitDeclaration(name="b1", bit=Bit("c", 1)),
            BitDeclaration(name="b2", bit=Bit("c", 2)),
            *extra_nodes,
        ]

    def _action(self, target_name, gate_name, args=None):
        return Action(
            target=target_name,
            instruction=GatePipeline(
                parts=[GateCall(name=gate_name, args=args or [])]
            ),
        )

    # SET
    def test_set_1(self):
        """b0 -> SET(1) must add a SetBits command."""
        circuit = Backend.compile_to_circuit(self._base(self._action("b0", "SET", [1])))
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_set_0(self):
        """b0 -> SET(0) must add a SetBits command."""
        circuit = Backend.compile_to_circuit(self._base(self._action("b0", "SET", [0])))
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_set_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(self._base(self._action("b0", "SET", [2])))

    def test_set_name_arg_raises(self):
        """SET with a NAME arg (not integer literal) must raise."""
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(self._base(self._action("b0", "SET", ["b1"])))

    # NOT
    def test_not_with_source(self):
        """b1 -> NOT(b0) must add one command."""
        circuit = Backend.compile_to_circuit(
            self._base(self._action("b1", "NOT", ["b0"]))
        )
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_not_wrong_arity_raises(self):
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(
                self._base(self._action("b2", "NOT", ["b0", "b1"]))
            )

    # COPY
    def test_copy(self):
        """b1 -> COPY(b0) must add one command."""
        circuit = Backend.compile_to_circuit(
            self._base(self._action("b1", "COPY", ["b0"]))
        )
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_copy_wrong_arity_raises(self):
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(self._base(self._action("b2", "COPY", [])))

    # AND / OR / XOR
    def test_and(self):
        """b2 -> AND(b0, b1) must add one command."""
        circuit = Backend.compile_to_circuit(
            self._base(self._action("b2", "AND", ["b0", "b1"]))
        )
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_or(self):
        """b2 -> OR(b0, b1) must add one command."""
        circuit = Backend.compile_to_circuit(
            self._base(self._action("b2", "OR", ["b0", "b1"]))
        )
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_xor(self):
        """b2 -> XOR(b0, b1) must add one command."""
        circuit = Backend.compile_to_circuit(
            self._base(self._action("b2", "XOR", ["b0", "b1"]))
        )
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_and_wrong_arity_raises(self):
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(self._base(self._action("b2", "AND", ["b0"])))

    # Unknown op
    def test_unknown_bit_op_raises(self):
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(self._base(self._action("b0", "NAND", ["b1"])))

    # Named pipelines on bit targets are expanded before dispatch, so they work.
    def test_named_pipeline_on_bit_works(self):
        """A named instruction whose gates are valid bit ops must expand and execute."""
        from spinachlang.spinach_types import GatePipeByName, InstructionDeclaration
        ast = [
            BitDeclaration(name="b0", bit=Bit("c", 0)),
            BitDeclaration(name="b1", bit=Bit("c", 1)),
            InstructionDeclaration(
                name="copy_op",
                pipeline=GatePipeline(parts=[GateCall(name="COPY", args=["b0"])]),
            ),
            Action(
                target="b1",
                instruction=GatePipeline(
                    parts=[GatePipeByName(name="copy_op", rev=False)]
                ),
            ),
        ]
        circuit = Backend.compile_to_circuit(ast)
        # COPY emits one classical command
        self.assertEqual(len(circuit.get_commands()), 1)


# ---------------------------------------------------------------------------
# 2. Classical bit operations via source code (parser round-trip)
# ---------------------------------------------------------------------------

class TestBitOpsSource(unittest.TestCase):
    """Full parse → AST → circuit round-trip for classical bit operations."""

    def test_set_from_source(self):
        code = """
        b0 : b 0
        b0 -> SET(1)
        """
        circuit = _circuit_from_source(code)
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_not_from_source(self):
        code = """
        b0 : b 0
        b1 : b 1
        b1 -> NOT(b0)
        """
        circuit = _circuit_from_source(code)
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_and_from_source(self):
        code = """
        b0 : b 0
        b1 : b 1
        b2 : b 2
        b2 -> AND(b0, b1)
        """
        circuit = _circuit_from_source(code)
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_or_from_source(self):
        code = """
        b0 : b 0
        b1 : b 1
        b2 : b 2
        b2 -> OR(b0, b1)
        """
        circuit = _circuit_from_source(code)
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_xor_from_source(self):
        code = """
        b0 : b 0
        b1 : b 1
        b2 : b 2
        b2 -> XOR(b0, b1)
        """
        circuit = _circuit_from_source(code)
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_copy_from_source(self):
        code = """
        b0 : b 0
        b1 : b 1
        b1 -> COPY(b0)
        """
        circuit = _circuit_from_source(code)
        self.assertTrue(len(circuit.get_commands()) >= 1)

    def test_mixed_qubit_and_bit_ops(self):
        """Mixing qubit gates and classical bit ops in one program."""
        code = """
        q0 : q 0
        b0 : b 0
        b1 : b 1
        b2 : b 2
        q0 -> H
        q0 -> M
        b2 -> AND(b0, b1)
        b1 -> NOT(b0)
        """
        circuit = _circuit_from_source(code)
        types = _op_types(circuit)
        self.assertIn(OpType.H, types)
        self.assertIn(OpType.Measure, types)
        # Two classical ops should also be present
        self.assertGreaterEqual(len(circuit.get_commands()), 4)

    def test_bit_ops_pipeline_count(self):
        """Each bit op generates exactly one command."""
        code = """
        b0 : b 0
        b1 : b 1
        b0 -> SET(1)
        b1 -> COPY(b0)
        """
        circuit = _circuit_from_source(code)
        self.assertEqual(len(circuit.get_commands()), 2)

    def test_repeat_count_on_bit_op(self):
        """'b0 -> 3 SET(1)' must generate 3 commands."""
        code = """
        b0 : b 0
        b0 -> 3 SET(1)
        """
        circuit = _circuit_from_source(code)
        self.assertEqual(len(circuit.get_commands()), 3)


# ---------------------------------------------------------------------------
# 3. BARRIER
# ---------------------------------------------------------------------------

class TestBarrier(unittest.TestCase):
    """BARRIER emits OpType.Barrier and is always a joint multi-qubit operation."""

    def test_single_qubit_barrier(self):
        """q0 -> BARRIER must produce one Barrier command."""
        code = """
        q0 : q 0
        q0 -> H
        q0 -> BARRIER
        q0 -> X
        """
        circuit = _circuit_from_source(code)
        types = _op_types(circuit)
        self.assertIn(OpType.Barrier, types)
        barrier_count = types.count(OpType.Barrier)
        self.assertEqual(barrier_count, 1)

    def test_list_target_barrier_is_joint(self):
        """[q0, q1] -> BARRIER must produce exactly ONE joint Barrier command."""
        code = """
        q0 : q 0
        q1 : q 1
        q0 -> H
        q1 -> X
        [q0, q1] -> BARRIER
        """
        circuit = _circuit_from_source(code)
        types = _op_types(circuit)
        barrier_count = types.count(OpType.Barrier)
        self.assertEqual(barrier_count, 1)

    def test_all_qubits_barrier(self):
        """* -> BARRIER must produce exactly ONE joint Barrier across all qubits."""
        code = """
        q0 : q 0
        q1 : q 1
        q2 : q 2
        q0 -> H
        q1 -> X
        q2 -> Z
        * -> BARRIER
        """
        circuit = _circuit_from_source(code)
        types = _op_types(circuit)
        barrier_count = types.count(OpType.Barrier)
        self.assertEqual(barrier_count, 1)

    def test_barrier_separates_gates(self):
        """Gates before and after barrier must all be present."""
        code = """
        q0 : q 0
        q0 -> H
        q0 -> BARRIER
        q0 -> X
        """
        circuit = _circuit_from_source(code)
        types = _op_types(circuit)
        self.assertEqual(types, [OpType.H, OpType.Barrier, OpType.X])

    def test_barrier_repeat_count(self):
        """q0 -> 2 BARRIER must produce exactly 2 Barrier commands."""
        code = """
        q0 : q 0
        q0 -> 2 BARRIER
        """
        circuit = _circuit_from_source(code)
        types = _op_types(circuit)
        self.assertEqual(types.count(OpType.Barrier), 2)

    def test_barrier_joint_qubit_count(self):
        """The joint barrier must reference all qubits in the target list."""
        code = """
        q0 : q 0
        q1 : q 1
        [q0, q1] -> BARRIER
        """
        circuit = _circuit_from_source(code)
        barriers = [
            cmd for cmd in circuit.get_commands()
            if cmd.op.type == OpType.Barrier
        ]
        self.assertEqual(len(barriers), 1)
        self.assertEqual(len(barriers[0].qubits), 2)


if __name__ == "__main__":
    unittest.main()

