"""Tests for the asp builder behaviour."""

import unittest

from lark import Tree

from pytket import Qubit, Bit

from spinachlang.ast_builder import AstBuilder


class TestAstBuilder(unittest.TestCase):
    """Tests for the asp builder behaviour."""

    def test_qubit_declaration(self):
        """Test qubit declaration"""
        tree = Tree("qubit_declaration", ["o_o", 5])
        result = AstBuilder().transform(tree)
        self.assertEqual(result.name, "o_o")
        self.assertEqual(result.qubit, Qubit(5))

    def test_bit_declaration(self):
        """Test bit declaration"""
        tree = Tree("bit_declaration", ["o_o", 5])
        result = AstBuilder().transform(tree)
        self.assertEqual(result.name, "o_o")
        self.assertEqual(result.bit, Bit(5))

    def test_list_declaration(self):
        """Test list declaration"""
        tree = Tree(
            "list_declaration", ["o_o", Tree("list", ["charl", "tom", "jerry"])]
        )
        result = AstBuilder().transform(tree)
        self.assertEqual(result.name, "o_o")
        self.assertEqual(result.items, ["charl", "tom", "jerry"])

    def test_pipeline_declaration(self):
        """Test pipeline declaration"""
        tree = Tree(
            "start",
            [
                Tree(
                    "statement",
                    [
                        Tree(
                            "declaration",
                            [
                                Tree(
                                    "instruction_declaration",
                                    [
                                        "o_o",
                                        Tree(
                                            "gate_pip",
                                            [
                                                Tree("gate_call", ["H"]),
                                                Tree(
                                                    "gate_call",
                                                    ["CX", Tree("args", [1])],
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        result = AstBuilder().transform(tree)
        first_instruction = result[0]
        self.assertEqual(first_instruction.name, "o_o")
        self.assertEqual(len(first_instruction.pipeline.parts), 2)
        self.assertEqual(first_instruction.pipeline.parts[0].name, "H")
        self.assertEqual(first_instruction.pipeline.parts[0].args, [])
        self.assertEqual(first_instruction.pipeline.parts[1].name, "CX")
        self.assertEqual(first_instruction.pipeline.parts[1].args, [1])

    def test_action(self):
        """Test actions"""
        tree = Tree(
            "start",
            [
                Tree(
                    "statement",
                    [
                        Tree(
                            "action",
                            [
                                "o_o",
                                "2",
                                Tree(
                                    "gate_pip",
                                    [
                                        Tree("gate_call", ["H"]),
                                        Tree("gate_call", ["X"]),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ],
        )
        result = AstBuilder().transform(tree)
        first_instruction = result[0]
        print(first_instruction)
        self.assertEqual(first_instruction.target, "o_o")
        self.assertEqual(first_instruction.count, 2)
        self.assertEqual(first_instruction.instruction.parts[0].name, "H")
        self.assertEqual(first_instruction.instruction.parts[1].name, "X")
