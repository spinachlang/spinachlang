"""Tests for SpinachFront parser behaviour."""

import logging
import unittest

from lark import Tree

from spinachlang.parser import Parser


class TestSpinachFront(unittest.TestCase):
    """Unit tests for SpinachFront"""

    def bit_naming(self):
        """Ensure bit declaration names and numbers parse correctly."""
        code = """
        alice : b 5

        """
        tree = Parser.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        self.assertEqual(tree.data, "start")

        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        bit = decl.children[0]
        self.assertIsInstance(bit, Tree)
        self.assertEqual(bit.data, "bit_declaration")

        name_node, number_node = bit.children

        self.assertEqual(name_node, "alice")

        self.assertEqual(number_node, "5")

    def test_qubit_explicit_naming(self):
        """Ensure qubit declaration parse correctly when explicit."""
        code = """
        bob : q 2

        """
        tree = Parser.get_tree(code=code)
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

        self.assertEqual(name_node, "bob")

        self.assertEqual(number_node, "2")

    def test_qubit_naming(self):
        """Ensure qubit declaration names and numbers parse correctly."""
        code = """
        tom : 3

        """
        tree = Parser.get_tree(code=code)
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
        tree = Parser.get_tree(code=code)
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
        tree = Parser.get_tree(code=code)
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
        tree = Parser.get_tree(code=code)
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

    def test_qubit_list_naming(self):
        """Ensure qubit list declaration names and numbers parse correctly."""
        code = """
        qlist : [alice, bob, tom]
        """
        tree = Parser.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        self.assertEqual(tree.data, "start")

        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        lst = decl.children[0]
        self.assertIsInstance(lst, Tree)
        self.assertEqual(lst.data, "list_declaration")

        name_node, items_node = lst.children

        self.assertEqual(name_node, "qlist")

        self.assertIsInstance(items_node, Tree)
        self.assertEqual(items_node.data, "list")
        items = items_node.children
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], "alice")
        self.assertEqual(items[1], "bob")
        self.assertEqual(items[2], "tom")

    def test_qubit_list_naming_with_numbers(self):
        """Ensure qubit list declaration with numbers parse correctly."""
        code = """
        qlist : [0, 1, 2]
        """
        tree = Parser.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        self.assertEqual(tree.data, "start")

        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        decl = statement.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        lst = decl.children[0]
        self.assertIsInstance(lst, Tree)
        self.assertEqual(lst.data, "list_declaration")

        name_node, items_node = lst.children

        self.assertEqual(name_node, "qlist")

        self.assertIsInstance(items_node, Tree)
        self.assertEqual(items_node.data, "list")
        items = items_node.children
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], "0")
        self.assertEqual(items[1], "1")
        self.assertEqual(items[2], "2")

    def test_action(self):
        """Ensure pipeline execution with gate before name parses correctly."""
        code = """
        o_o -> 2 H | name1
        """
        tree = Parser.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        execution = statement.children[0]
        self.assertIsInstance(execution, Tree)
        self.assertEqual(execution.data, "action")
        target_node, count_node, instruction_node = execution.children
        self.assertEqual(target_node, "o_o")
        self.assertEqual(count_node, "2")
        self.assertEqual(instruction_node.data, "gate_pip")
        self.assertIsInstance(instruction_node.children[0], Tree)
        self.assertIsInstance(instruction_node.children[1], Tree)
        gate_call = instruction_node.children[0]
        gate_call_name = instruction_node.children[1]
        self.assertEqual(gate_call_name.children[0], "name1")
        self.assertEqual(gate_call.data, "gate_call")
        self.assertEqual(gate_call.children[0], "H")

    def test_action_with_list(self):
        """Ensure pipeline execution with list target parses correctly."""
        code = """
        [1, 2, 3] -> H | name1
        """
        tree = Parser.get_tree(code=code)
        logging.debug("tree: %s", tree.pretty())
        statement = tree.children[0]
        self.assertIsInstance(statement, Tree)
        self.assertEqual(statement.data, "statement")
        execution = statement.children[0]
        self.assertIsInstance(execution, Tree)
        self.assertEqual(execution.data, "action")
        target_node, count_node, instruction_node = execution.children
        self.assertIsInstance(target_node, Tree)
        self.assertEqual(target_node.data, "list")
        items = target_node.children
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], "1")
        self.assertEqual(items[1], "2")
        self.assertEqual(items[2], "3")
        self.assertIsNone(count_node)
        self.assertEqual(instruction_node.data, "gate_pip")
        self.assertIsInstance(instruction_node.children[0], Tree)
        self.assertIsInstance(instruction_node.children[1], Tree)
        gate_call = instruction_node.children[0]
        gate_call_name = instruction_node.children[1]
        self.assertEqual(gate_call_name.children[0], "name1")
        self.assertEqual(gate_call.data, "gate_call")
        self.assertEqual(gate_call.children[0], "H")
