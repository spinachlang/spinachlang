"""Tests for SpinachFront parser behaviour."""

import logging
import unittest

from lark import Tree

from app.frontend.spinach_front import SpinachFront


class TestSpinachFront(unittest.TestCase):
    """Unit tests for SpinachFront"""

    def test_qubit_naming(self):
        """Ensure qubit declaration names and numbers parse correctly."""
        code = """
        tom : 3

        """
        tree = SpinachFront.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        self.assertEqual(tree.data, "start")

        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        qubit = decl.children[0]
        self.assertIsInstance(qubit, Tree)
        self.assertEqual(qubit.data, "qubit_declaration")

        name_node, number_node = qubit.children

        self.assertEqual(name_node, "tom")

        self.assertEqual(number_node, "3")

    def test_pipeline_naming(self):
        """Ensure pipeline with gate before name parses correctly."""
        code = """
        o_o : H | name1
        """
        tree = SpinachFront.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        instruction = decl.children[0]
        self.assertIsInstance(instruction, Tree)
        self.assertEqual(instruction.data, "instruction_declaration")
        name_node, instruction_node = instruction.children
        self.assertEqual(name_node, "o_o")
        self.assertEqual(instruction_node.data, "gate_pip")
        self.assertIsInstance(instruction_node.children[0], Tree)
        self.assertIsInstance(instruction_node.children[1], Tree)
        gate_call = instruction_node.children[0]
        gate_call_name = instruction_node.children[1]
        self.assertEqual(gate_call_name.children[0], "name1")

        self.assertEqual(gate_call.data, "gate_call")
        self.assertEqual(gate_call.children[0], "H")

    def test_pipeline_naming_with_reverse(self):
        """Ensure pipeline with reverse operator parses correctly."""
        code = """
        o_o : name1 <-
        """
        tree = SpinachFront.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")

        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        instruction = decl.children[0]
        self.assertIsInstance(instruction, Tree)
        self.assertEqual(instruction.data, "instruction_declaration")
        name_node, instruction_node = instruction.children
        self.assertEqual(name_node, "o_o")
        self.assertEqual(instruction_node.data, "gate_pip")
        self.assertIsInstance(instruction_node.children[0], Tree)
        gate_call_name = instruction_node.children[0]
        self.assertEqual(gate_call_name.children[0], "name1")
        self.assertEqual(gate_call_name.children[1], "<-")

    def test_pipeline_naming_with_name_at_first(self):
        """Ensure pipeline with name before gate parses correctly."""
        code = """
        o_o : name1 | H
        """
        tree = SpinachFront.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        instruction = decl.children[0]
        self.assertIsInstance(instruction, Tree)
        self.assertEqual(instruction.data, "instruction_declaration")
        name_node, instruction_node = instruction.children
        self.assertEqual(name_node, "o_o")
        self.assertEqual(instruction_node.data, "gate_pip")
        self.assertIsInstance(instruction_node.children[1], Tree)
        self.assertIsInstance(instruction_node.children[0], Tree)
        gate_call = instruction_node.children[1]
        gate_call_name = instruction_node.children[0]
        self.assertEqual(gate_call_name.children[0], "name1")

        self.assertEqual(gate_call.data, "gate_call")
        self.assertEqual(gate_call.children[0], "H")
