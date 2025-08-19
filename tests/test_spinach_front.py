from app.frontend.spinach_front import SpinachFront
from lark import Tree
import unittest
import logging


class TestSpinachFront(unittest.TestCase):
    def test_qubit_naming(self):
        code = """
        tom : 3
        
        """
        tree = SpinachFront.get_tree(code=code)
        logging.debug("tree: " + tree.pretty())
        self.assertEqual(tree.data, "statement")

        decl = tree.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        qubit = decl.children[0]
        self.assertIsInstance(qubit, Tree)
        self.assertEqual(qubit.data, "qubit_declaration")

        name_node, number_node = qubit.children

        self.assertEqual(name_node.data, "name")
        self.assertEqual(name_node.children[0], "tom")

        self.assertEqual(number_node.data, "number")
        self.assertEqual(number_node.children[0], "3")

    def test_pipeline_naming(self):
        code = """
        o_o : H | name1
        """
        tree = SpinachFront.get_tree(code=code)
        logging.debug("tree: " + tree.pretty())
        decl = tree.children[0]
        self.assertIsInstance(decl, Tree)
        self.assertEqual(decl.data, "declaration")

        instruction = decl.children[0]
        self.assertIsInstance(instruction, Tree)
        self.assertEqual(instruction.data, "instruction_declaration")
        name_node, instruction_node = instruction.children
        self.assertEqual(name_node.data, "name")
        self.assertEqual(name_node.children[0], "o_o")
        self.assertEqual(instruction_node.data, "gate_pip")
        self.assertIsInstance(instruction_node.children[0], Tree)
        self.assertIsInstance(instruction_node.children[1], Tree)
        gate_call = instruction_node.children[0]
        gate_call_name = instruction_node.children[1]
        self.assertEqual(gate_call_name.data, "name")
        self.assertEqual(gate_call_name.children[0], "name1")

        self.assertEqual(gate_call.data, "gate_call")
        self.assertIsInstance(gate_call.children[0], Tree)
        self.assertEqual(gate_call.children[0].data, "upper_name")
        self.assertEqual(gate_call.children[0].children[0], "H")
