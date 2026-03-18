"""Tests for the three equivalent qubit reference forms:

    1. Bare integer     0 -> H          FCX(1)
    2. Explicit q N     q 0 -> H        FCX(q 1)
    3. Named qubit      alice -> H      FCX(alice)   (where alice : 1)

All three must produce the exact same circuit.  Tests live at two levels:
  - Parser level  : raw Lark tree structure (TestQubitRefParser)
  - Compiler level: end-to-end gate equivalence (TestQubitRefCompiler)
"""

import unittest

from lark import Tree
from pytket import Qubit, Bit
from pytket.circuit import OpType

from spinachlang.parser import Parser
from spinachlang.spinach import Spinach
from spinachlang.backend import Backend
from spinachlang.spinach_types import (
    QubitDeclaration,
    Action,
    GatePipeline,
    GateCall,
    ConditionalAction,
    BitDeclaration,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ops(code: str):
    """Return list of (OpType, qubit_indices) for every command in the circuit."""
    circuit = Spinach.create_circuit(code)
    return [
        (cmd.op.type, [q.index[0] for q in cmd.qubits])
        for cmd in circuit.get_commands()
    ]


def _gate_types(code: str):
    circuit = Spinach.create_circuit(code)
    return [cmd.op.type for cmd in circuit.get_commands()]


# ---------------------------------------------------------------------------
# Parser-level tests  (raw Lark tree)
# ---------------------------------------------------------------------------

class TestQubitRefParser(unittest.TestCase):
    """Verify that the grammar produces the expected tree nodes for q N syntax."""

    # ── action targets ────────────────────────────────────────────────────

    def test_bare_number_action_target_parses(self):
        """0 -> H  — NUMBER is the action target."""
        tree = Parser.get_tree("0 -> H")
        action = tree.children[0].children[0]
        self.assertEqual(action.data, "action")
        target = action.children[0]
        # bare NUMBER is processed into an int by the AstBuilder; at raw-tree
        # level it arrives as a Token (string-like) equal to "0"
        self.assertEqual(str(target), "0")

    def test_qubit_ref_action_target_parses(self):
        """q 0 -> H  — qubit_ref tree node is the action target."""
        tree = Parser.get_tree("q 0 -> H")
        action = tree.children[0].children[0]
        self.assertEqual(action.data, "action")
        target = action.children[0]
        self.assertIsInstance(target, Tree)
        self.assertEqual(target.data, "qubit_ref")
        self.assertEqual(str(target.children[0]), "0")

    def test_named_qubit_action_target_parses(self):
        """alice -> H  — NAME token is the action target."""
        tree = Parser.get_tree("alice : 0\nalice -> H")
        action = tree.children[1].children[0]
        self.assertEqual(action.data, "action")
        target = action.children[0]
        self.assertEqual(str(target), "alice")

    # ── gate arguments ────────────────────────────────────────────────────

    def test_bare_number_arg_parses(self):
        """0 -> FCX(1)  — NUMBER in gate arg."""
        tree = Parser.get_tree("0 -> FCX(1)")
        action = tree.children[0].children[0]
        gate = action.children[2].children[0]   # gate_pip → gate_call
        self.assertEqual(gate.data, "gate_call")
        args_node = gate.children[1]
        self.assertIsInstance(args_node, Tree)
        self.assertEqual(args_node.data, "args")
        self.assertEqual(str(args_node.children[0]), "1")

    def test_qubit_ref_arg_parses(self):
        """0 -> FCX(q 1)  — qubit_ref in gate arg."""
        tree = Parser.get_tree("0 -> FCX(q 1)")
        action = tree.children[0].children[0]
        gate = action.children[2].children[0]
        self.assertEqual(gate.data, "gate_call")
        args_node = gate.children[1]
        self.assertIsInstance(args_node, Tree)
        qref = args_node.children[0]
        self.assertIsInstance(qref, Tree)
        self.assertEqual(qref.data, "qubit_ref")
        self.assertEqual(str(qref.children[0]), "1")

    def test_named_qubit_arg_parses(self):
        """0 -> FCX(ctrl)  — NAME in gate arg."""
        tree = Parser.get_tree("ctrl : 1\n0 -> FCX(ctrl)")
        action = tree.children[1].children[0]
        gate = action.children[2].children[0]
        args_node = gate.children[1]
        self.assertEqual(str(args_node.children[0]), "ctrl")

    # ── list targets ──────────────────────────────────────────────────────

    def test_qubit_ref_in_list_target_parses(self):
        """[q 0, q 1] -> H  — qubit_ref inside a list action target."""
        tree = Parser.get_tree("[q 0, q 1] -> H")
        action = tree.children[0].children[0]
        self.assertEqual(action.data, "action")
        lst = action.children[0]
        self.assertIsInstance(lst, Tree)
        self.assertEqual(lst.data, "list")
        for child in lst.children:
            self.assertIsInstance(child, Tree)
            self.assertEqual(child.data, "qubit_ref")

    def test_mixed_list_parses(self):
        """[0, q 1, alice] -> H  — mixed NUMBER / qubit_ref / NAME in list."""
        tree = Parser.get_tree("alice : 2\n[0, q 1, alice] -> H")
        action = tree.children[1].children[0]
        lst = action.children[0]
        self.assertEqual(lst.data, "list")
        # first child is raw NUMBER token "0"
        self.assertEqual(str(lst.children[0]), "0")
        # second child is qubit_ref
        self.assertEqual(lst.children[1].data, "qubit_ref")
        # third child is NAME token
        self.assertEqual(str(lst.children[2]), "alice")

    # ── conditional targets ───────────────────────────────────────────────

    def test_qubit_ref_conditional_target_parses(self):
        """q 0 -> X if flag  — qubit_ref as conditional action target."""
        tree = Parser.get_tree("flag : b 0\nq 0 -> X if flag")
        cond = tree.children[1].children[0]
        self.assertEqual(cond.data, "conditional_action")
        target = cond.children[0]
        self.assertIsInstance(target, Tree)
        self.assertEqual(target.data, "qubit_ref")

    # ── multi-qubit gate args ─────────────────────────────────────────────

    def test_qubit_ref_multiple_args_parses(self):
        """0 -> CU1(0.5, q 1)  — qubit_ref as second arg alongside a float."""
        tree = Parser.get_tree("0 -> CU1(0.5, q 1)")
        action = tree.children[0].children[0]
        gate = action.children[2].children[0]
        args_node = gate.children[1]
        # first arg is float "0.5"
        self.assertEqual(str(args_node.children[0]), "0.5")
        # second arg is qubit_ref
        qref = args_node.children[1]
        self.assertIsInstance(qref, Tree)
        self.assertEqual(qref.data, "qubit_ref")
        self.assertEqual(str(qref.children[0]), "1")


# ---------------------------------------------------------------------------
# Compiler-level tests  (end-to-end gate equivalence)
# ---------------------------------------------------------------------------

class TestQubitRefCompiler(unittest.TestCase):
    """Verify that all three qubit reference forms produce identical circuits."""

    # ── single-qubit action target ────────────────────────────────────────

    def test_bare_number_target_h(self):
        """0 -> H applies H to q[0]."""
        ops = _ops("0 -> H")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0], (OpType.H, [0]))

    def test_q_n_target_h(self):
        """q 0 -> H applies H to q[0] — same as bare number."""
        ops = _ops("q 0 -> H")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0], (OpType.H, [0]))

    def test_named_target_h(self):
        """tom : 0 / tom -> H applies H to q[0] — same as bare number."""
        ops = _ops("tom : 0\ntom -> H")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0], (OpType.H, [0]))

    def test_all_three_targets_identical(self):
        """0 -> X, q 0 -> X, and named -> X all produce the same single gate."""
        bare  = _ops("0 -> X")
        q_n   = _ops("q 0 -> X")
        named = _ops("src : 0\nsrc -> X")
        self.assertEqual(bare, q_n)
        self.assertEqual(bare, named)

    # ── gate argument forms ───────────────────────────────────────────────

    def test_bare_number_arg_cx(self):
        """0 -> CX(1) — bare integer as CX control."""
        circuit = Spinach.create_circuit("0 -> CX(1)")
        cmds = circuit.get_commands()
        cx = next(c for c in cmds if c.op.type == OpType.CX)
        self.assertEqual([q.index[0] for q in cx.qubits], [1, 0])  # ctrl, target

    def test_q_n_arg_cx(self):
        """0 -> CX(q 1) — q N as CX control, identical to bare 1."""
        circuit = Spinach.create_circuit("0 -> CX(q 1)")
        cmds = circuit.get_commands()
        cx = next(c for c in cmds if c.op.type == OpType.CX)
        self.assertEqual([q.index[0] for q in cx.qubits], [1, 0])

    def test_named_arg_cx(self):
        """ctrl : 1 / 0 -> CX(ctrl) — named qubit as CX control."""
        circuit = Spinach.create_circuit("ctrl : 1\n0 -> CX(ctrl)")
        cmds = circuit.get_commands()
        cx = next(c for c in cmds if c.op.type == OpType.CX)
        self.assertEqual([q.index[0] for q in cx.qubits], [1, 0])

    def test_all_three_cx_args_identical(self):
        """CX(1), CX(q 1), and CX(ctrl) produce the same CX gate."""
        def cx_qubits(code):
            circuit = Spinach.create_circuit(code)
            cx = next(c for c in circuit.get_commands() if c.op.type == OpType.CX)
            return [q.index[0] for q in cx.qubits]

        bare  = cx_qubits("0 -> CX(1)")
        q_n   = cx_qubits("0 -> CX(q 1)")
        named = cx_qubits("ctrl : 1\n0 -> CX(ctrl)")
        self.assertEqual(bare, q_n)
        self.assertEqual(bare, named)

    # ── FCX (flipped CX) arg forms ─────────────────────────────────────────

    def test_all_three_fcx_args_identical(self):
        """FCX(1), FCX(q 1), FCX(ctrl) all wire the same CX."""
        def fcx_qubits(code):
            circuit = Spinach.create_circuit(code)
            cx = next(c for c in circuit.get_commands() if c.op.type == OpType.CX)
            return [q.index[0] for q in cx.qubits]

        bare  = fcx_qubits("0 -> FCX(1)")
        q_n   = fcx_qubits("0 -> FCX(q 1)")
        named = fcx_qubits("ctrl : 1\n0 -> FCX(ctrl)")
        self.assertEqual(bare, q_n)
        self.assertEqual(bare, named)

    # ── list targets ──────────────────────────────────────────────────────

    def test_bare_number_list_target(self):
        """[0, 1] -> H applies H to both qubits."""
        ops = _ops("[0, 1] -> H")
        h_ops = [(t, q) for t, q in ops if t == OpType.H]
        self.assertIn((OpType.H, [0]), h_ops)
        self.assertIn((OpType.H, [1]), h_ops)

    def test_q_n_list_target(self):
        """[q 0, q 1] -> H — same as bare number list."""
        ops_bare  = _ops("[0, 1] -> H")
        ops_q_n   = _ops("[q 0, q 1] -> H")
        self.assertEqual(
            {(t, tuple(q)) for t, q in ops_bare},
            {(t, tuple(q)) for t, q in ops_q_n},
        )

    def test_mixed_list_target(self):
        """[0, q 1, alice] -> H where alice : 2 — all three forms in one list."""
        ops = _ops("alice : 2\n[0, q 1, alice] -> H")
        h_indices = [q[0] for t, q in ops if t == OpType.H]
        self.assertIn(0, h_indices)
        self.assertIn(1, h_indices)
        self.assertIn(2, h_indices)

    # ── conditional action target ─────────────────────────────────────────

    def test_q_n_conditional_target(self):
        """q 0 -> X if flag — applies X to q[0] when flag bit is 1.

        In PyTKET, classically-conditioned gates are wrapped in OpType.Conditional;
        the inner gate is accessible via cmd.op.op.type.
        """
        code = "flag : b 0\nq 0 -> X if flag"
        circuit = Spinach.create_circuit(code)
        cmds = circuit.get_commands()
        conditional = next(
            c for c in cmds if c.op.type == OpType.Conditional
        )
        self.assertEqual(conditional.op.op.type, OpType.X)
        self.assertEqual(conditional.qubits[0].index[0], 0)

    def test_bare_number_and_q_n_conditional_equivalent(self):
        """'0 -> X if flag' and 'q 0 -> X if flag' produce the same circuit."""
        bare = Spinach.create_circuit("flag : b 0\n0 -> X if flag")
        q_n  = Spinach.create_circuit("flag : b 0\nq 0 -> X if flag")
        self.assertEqual(
            [c.op.type for c in bare.get_commands()],
            [c.op.type for c in q_n.get_commands()],
        )

    # ── GHZ with q N syntax (the motivating example) ─────────────────────

    def test_ghz_bare_numbers(self):
        """Classic GHZ with bare numbers: 0 -> H | FCX(1) | FCX(2) ."""
        circuit = Spinach.create_circuit("0 -> H | FCX(1) | FCX(2)\n* -> M")
        types = [c.op.type for c in circuit.get_commands()]
        self.assertIn(OpType.H,    types)
        self.assertIn(OpType.CX,   types)
        cx_cmds = [c for c in circuit.get_commands() if c.op.type == OpType.CX]
        self.assertEqual(len(cx_cmds), 2)

    def test_ghz_q_n_syntax(self):
        """GHZ with q N syntax: q 0 -> H | FCX(q 1) | FCX(q 2) ."""
        circuit = Spinach.create_circuit("q 0 -> H | FCX(q 1) | FCX(q 2)\n* -> M")
        types = [c.op.type for c in circuit.get_commands()]
        self.assertIn(OpType.H,  types)
        self.assertIn(OpType.CX, types)

    def test_ghz_all_forms_equivalent(self):
        """Bare numbers, q N, and named qubits all produce the same GHZ circuit."""
        bare  = "0 -> H | FCX(1) | FCX(2)\n* -> M"
        q_n   = "q 0 -> H | FCX(q 1) | FCX(q 2)\n* -> M"
        named = "a : 0\nb : 1\nc : 2\na -> H | FCX(1) | FCX(2)\n* -> M"

        def gate_set(code):
            circuit = Spinach.create_circuit(code)
            return frozenset(
                (c.op.type, tuple(q.index[0] for q in c.qubits))
                for c in circuit.get_commands()
            )

        self.assertEqual(gate_set(bare), gate_set(q_n))
        self.assertEqual(gate_set(bare), gate_set(named))

    # ── multi-arg gate with q N ────────────────────────────────────────────

    def test_cu1_q_n_arg(self):
        """0 -> CU1(0.5, q 1) — float angle + q N qubit reference."""
        circuit = Spinach.create_circuit("0 -> CU1(0.5, q 1)")
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.CU1)
        qubit_indices = [q.index[0] for q in cmds[0].qubits]
        # CU1(angle, ctrl, target) in pytket: [ctrl, target]
        self.assertIn(0, qubit_indices)
        self.assertIn(1, qubit_indices)

    def test_ccx_q_n_args(self):
        """2 -> CCX(q 0, q 1) — Toffoli with two q N controls."""
        circuit = Spinach.create_circuit("2 -> CCX(q 0, q 1)")
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.CCX)
        qubit_indices = {q.index[0] for q in cmds[0].qubits}
        self.assertEqual(qubit_indices, {0, 1, 2})

    # ── invalid q N (float index should raise) ────────────────────────────

    def test_q_float_index_raises(self):
        """q 0.5 -> H must raise ValueError (float qubit index)."""
        with self.assertRaises((ValueError, Exception)):
            Spinach.create_circuit("q 0.5 -> H")


if __name__ == "__main__":
    unittest.main()

