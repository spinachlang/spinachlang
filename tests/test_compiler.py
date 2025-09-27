"""Test the compiling code getting the ast and creating a tket circuit"""

import unittest


from pytket import Qubit, Bit

from pytket.circuit import OpType

from spinachlang.spinach_types import (
    QubitDeclaration,
    ListDeclaration,
    BitDeclaration,
    InstructionDeclaration,
    Action,
    GateCall,
    GatePipeByName,
    GatePipeline,
)

from spinachlang.backend import Backend


class TestCompiler(unittest.TestCase):
    """Test the compiling code getting the ast and creating a tket circuit"""

    def test_simple_action(self):
        """test this code: 1 -> H"""
        ast = [
            Action(
                target=1,
                count=None,
                instruction=GatePipeline(parts=[GateCall(name="H", args=[])]),
            )
        ]
        result = Backend.compile_to_circuit(ast)
        commands = result.get_commands()
        self.assertEqual(len(commands), 1)
        cmd = commands[0]

        self.assertEqual(cmd.op.type, OpType.H)
        self.assertEqual(cmd.qubits, [Qubit(1)])

    def test_action_with_named_qubit(self):
        """test this code:
        tom : q 2
        tom -> X
        """
        ast = [
            QubitDeclaration(name="tom", qubit=Qubit(2)),
            Action(
                target="tom",
                count=None,
                instruction=GatePipeline(parts=[GateCall(name="X", args=[])]),
            ),
        ]
        result = Backend.compile_to_circuit(ast)
        commands = result.get_commands()
        self.assertEqual(len(commands), 1)
        cmd = commands[0]
        self.assertEqual(cmd.op.type, OpType.X)
        self.assertEqual(cmd.qubits, [Qubit(2)])

    def test_named_pipelines(self):
        """test this code:
        superman : Z | X | H
        3 -> superman | superman <- | M
        """
        ast = [
            InstructionDeclaration(
                name="superman",
                pipeline=GatePipeline(
                    parts=[
                        GateCall(name="Z", args=[]),
                        GateCall(name="X", args=[]),
                        GateCall(name="H", args=[]),
                    ]
                ),
            ),
            Action(
                target=3,
                instruction=GatePipeline(
                    parts=[
                        GatePipeByName(name="superman", rev=False),
                        GatePipeByName(name="superman", rev=True),
                        GateCall(name="M", args=[]),
                    ]
                ),
            ),
        ]
        result = Backend.compile_to_circuit(ast)
        commands = result.get_commands()
        self.assertEqual(len(commands), 7)
        self.assertEqual(commands[0].op.type, OpType.Z)
        self.assertEqual(commands[1].op.type, OpType.X)
        self.assertEqual(commands[2].op.type, OpType.H)
        self.assertEqual(commands[3].op.type, OpType.H)
        self.assertEqual(commands[4].op.type, OpType.X)
        self.assertEqual(commands[5].op.type, OpType.Z)
        self.assertEqual(commands[6].op.type, OpType.Measure)
        for cmd in commands:
            self.assertEqual(cmd.qubits, [Qubit(3)])

    @unittest.expectedFailure
    def test_named_list_as_action_target(self):
        """test this code:
        dracula : [1, 3]
        dracula -> H
        """
        ast = [
            ListDeclaration(name="dracula", items=[1, 3]),
            Action(
                target="dracula",
                count=2,
                instruction=GatePipeline(parts=[GateCall(name="H", args=[])]),
            ),
        ]

    def test_list_as_action_target(self):
        """test this code:
        [2, 1] -> H
        """
        ast = [
            Action(
                target=[2, 1],
                count=1,
                instruction=GatePipeline(parts=[GateCall(name="H", args=[])]),
            ),
        ]
        result = Backend.compile_to_circuit(ast)
        commands = result.get_commands()
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].op.type, OpType.H)
        self.assertEqual(commands[1].op.type, OpType.H)
        self.assertEqual(commands[0].qubits, [Qubit(1)])
        self.assertEqual(commands[1].qubits, [Qubit(2)])
