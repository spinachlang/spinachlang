"""Tests for the two critical features:
  1. Bit declaration reachable from source (grammar fix)
  2. Classically conditional actions  (if / if-else)
"""

import unittest

from pytket import Qubit, Bit
from pytket.circuit import OpType

from spinachlang.spinach import Spinach
from spinachlang.parser import Parser
from spinachlang.ast_builder import AstBuilder
from spinachlang.backend import Backend
from spinachlang.spinach_types import (
    BitDeclaration,
    QubitDeclaration,
    ConditionalAction,
    GatePipeline,
    GateCall,
)


# ---------------------------------------------------------------------------
# 1. Bit declaration
# ---------------------------------------------------------------------------

class TestBitDeclaration(unittest.TestCase):
    """bit_declaration is now reachable from the declaration rule."""

    def test_bit_declaration_parses(self):
        """'result : b 0' must produce a bit_declaration tree node."""
        tree = Parser.get_tree("result : b 0")
        decl = tree.children[0].children[0]           # statement → declaration
        self.assertEqual(decl.data, "declaration")
        bit_node = decl.children[0]
        self.assertEqual(bit_node.data, "bit_declaration")
        self.assertEqual(str(bit_node.children[0]), "result")
        self.assertEqual(str(bit_node.children[1]), "0")

    def test_bit_declaration_builds_ast(self):
        """AstBuilder must produce a BitDeclaration from source."""
        nodes = AstBuilder().transform(Parser.get_tree("result : b 0"))
        self.assertEqual(len(nodes), 1)
        node = nodes[0]
        self.assertIsInstance(node, BitDeclaration)
        self.assertEqual(node.name, "result")
        self.assertEqual(node.bit, Bit("c", 0))

    def test_bit_declaration_registers_in_index(self):
        """compile_to_circuit must put the Bit in the circuit's bit list."""
        code = """
        q0 : q 0
        result : b 0
        q0 -> M
        """
        circuit = Spinach.create_circuit(code)
        self.assertIn(Bit("c", 0), circuit.bits)

    def test_multiple_bits_and_qubits(self):
        """Multiple bit and qubit declarations co-exist without error."""
        code = """
        alice : q 0
        bob   : q 1
        ca    : b 0
        cb    : b 1
        alice -> H
        bob   -> X
        alice -> M
        bob   -> M
        """
        circuit = Spinach.create_circuit(code)
        self.assertIn(Qubit("q", 0), circuit.qubits)
        self.assertIn(Qubit("q", 1), circuit.qubits)


# ---------------------------------------------------------------------------
# 2. Classically conditional actions
# ---------------------------------------------------------------------------

class TestConditionalActionType(unittest.TestCase):
    """ConditionalAction type and backend compilation."""

    def _simple_circuit_with_bit(self):
        """Return (circuit, index) with one qubit and one bit already in circuit."""
        from pytket import Circuit
        c = Circuit()
        q = Qubit("q", 0)
        b = Bit("c", 0)
        c.add_qubit(q)
        c.add_bit(b)
        return c, {"q0": q, "b0": b}

    def test_if_only_emits_conditional_gate(self):
        """if-only action must emit exactly one Conditional(X) command."""
        c, index = self._simple_circuit_with_bit()
        action = ConditionalAction(
            target="q0",
            condition_bit="b0",
            if_pipeline=GatePipeline(parts=[GateCall(name="X")]),
        )
        Backend.compile_to_circuit([
            QubitDeclaration(name="q0", qubit=Qubit("q", 0)),
            BitDeclaration(name="b0", bit=Bit("c", 0)),
            action,
        ])
        # Re-compile via full pipeline so circuit is fresh
        ast = [
            QubitDeclaration(name="q0", qubit=Qubit("q", 0)),
            BitDeclaration(name="b0", bit=Bit("c", 0)),
            ConditionalAction(
                target="q0",
                condition_bit="b0",
                if_pipeline=GatePipeline(parts=[GateCall(name="X")]),
            ),
        ]
        circuit = Backend.compile_to_circuit(ast)
        commands = circuit.get_commands()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].op.type, OpType.Conditional)

    def test_if_else_emits_two_conditional_gates(self):
        """if/else action must emit two Conditional commands (value 1 then 0)."""
        ast = [
            QubitDeclaration(name="q0", qubit=Qubit("q", 0)),
            BitDeclaration(name="b0", bit=Bit("c", 0)),
            ConditionalAction(
                target="q0",
                condition_bit="b0",
                if_pipeline=GatePipeline(parts=[GateCall(name="X")]),
                else_pipeline=GatePipeline(parts=[GateCall(name="Z")]),
            ),
        ]
        circuit = Backend.compile_to_circuit(ast)
        commands = circuit.get_commands()
        self.assertEqual(len(commands), 2)
        self.assertTrue(all(cmd.op.type == OpType.Conditional for cmd in commands))

    def test_unknown_condition_bit_raises(self):
        """Referencing an undeclared bit as condition must raise ValueError."""
        ast = [
            QubitDeclaration(name="q0", qubit=Qubit("q", 0)),
            ConditionalAction(
                target="q0",
                condition_bit="ghost",
                if_pipeline=GatePipeline(parts=[GateCall(name="X")]),
            ),
        ]
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(ast)

    def test_condition_on_qubit_raises(self):
        """Using a qubit name as condition bit must raise ValueError."""
        ast = [
            QubitDeclaration(name="q0", qubit=Qubit("q", 0)),
            ConditionalAction(
                target="q0",
                condition_bit="q0",   # q0 is a Qubit, not a Bit
                if_pipeline=GatePipeline(parts=[GateCall(name="X")]),
            ),
        ]
        with self.assertRaises(ValueError):
            Backend.compile_to_circuit(ast)


class TestConditionalActionParser(unittest.TestCase):
    """Full parse → AST → circuit round-trip for conditional syntax."""

    def test_if_only_parses(self):
        """'q0 -> X if b0' must parse into a conditional_action tree node."""
        tree = Parser.get_tree("q0 : q 0\nb0 : b 0\nq0 -> X if b0")
        # third statement is the conditional action
        stmt = tree.children[2].children[0]
        self.assertEqual(stmt.data, "conditional_action")

    def test_if_else_parses(self):
        """'q0 -> X if b0 else Z' must parse into a conditional_action tree node."""
        tree = Parser.get_tree("q0 : q 0\nb0 : b 0\nq0 -> X if b0 else Z")
        stmt = tree.children[2].children[0]
        self.assertEqual(stmt.data, "conditional_action")

    def test_if_only_compiles(self):
        """Full source with if-only conditional must produce a Conditional command."""
        code = """
        q0 : q 0
        b0 : b 0
        q0 -> M
        q0 -> X if b0
        """
        circuit = Spinach.create_circuit(code)
        types = [cmd.op.type for cmd in circuit.get_commands()]
        self.assertIn(OpType.Measure, types)
        self.assertIn(OpType.Conditional, types)

    def test_if_else_compiles(self):
        """Full source with if/else conditional must produce two Conditional commands."""
        code = """
        q0 : q 0
        b0 : b 0
        q0 -> M
        q0 -> X if b0 else Z
        """
        circuit = Spinach.create_circuit(code)
        conditionals = [
            cmd for cmd in circuit.get_commands()
            if cmd.op.type == OpType.Conditional
        ]
        self.assertEqual(len(conditionals), 2)

    def test_multi_gate_if_branch_with_parens(self):
        """'q0 -> (H | X) if b0' must apply both H and X conditionally."""
        code = """
        q0 : q 0
        b0 : b 0
        q0 -> M
        q0 -> (H | X) if b0
        """
        circuit = Spinach.create_circuit(code)
        conditionals = [
            cmd for cmd in circuit.get_commands()
            if cmd.op.type == OpType.Conditional
        ]
        self.assertEqual(len(conditionals), 2)

    def test_multi_gate_if_else_with_parens(self):
        """'q0 -> (H | X) if b0 else (Z | S)' must yield four Conditional commands."""
        code = """
        q0 : q 0
        b0 : b 0
        q0 -> M
        q0 -> (H | X) if b0 else (Z | S)
        """
        circuit = Spinach.create_circuit(code)
        conditionals = [
            cmd for cmd in circuit.get_commands()
            if cmd.op.type == OpType.Conditional
        ]
        self.assertEqual(len(conditionals), 4)

    def test_named_instruction_in_if_branch(self):
        """A named instruction used in a conditional branch must expand correctly."""
        code = """
        q0   : q 0
        b0   : b 0
        flip : X | Z
        q0 -> M
        q0 -> flip if b0
        """
        circuit = Spinach.create_circuit(code)
        conditionals = [
            cmd for cmd in circuit.get_commands()
            if cmd.op.type == OpType.Conditional
        ]
        # flip expands to X then Z → 2 conditional gates
        self.assertEqual(len(conditionals), 2)

    def test_teleportation_pattern(self):
        """Quantum teleportation feedforward: X if b0, Z if b1."""
        code = """
        target : q 0
        b0     : b 0
        b1     : b 1
        target -> X if b0
        target -> Z if b1
        """
        circuit = Spinach.create_circuit(code)
        conditionals = [
            cmd for cmd in circuit.get_commands()
            if cmd.op.type == OpType.Conditional
        ]
        self.assertEqual(len(conditionals), 2)


if __name__ == "__main__":
    unittest.main()

