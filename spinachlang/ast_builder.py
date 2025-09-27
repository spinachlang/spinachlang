"""Abstract syntax tree builder"""

from typing import Union, List
from pytket import Qubit, Bit
from lark import Transformer, v_args

from .spinach_types import (
    GatePipeByName,
    GatePipeline,
    GateCall,
    Action,
    QubitDeclaration,
    BitDeclaration,
    ListDeclaration,
    InstructionDeclaration,
)


class AstBuilder(Transformer):
    """Abstract syntax tree builder"""

    def __init__(self):
        super().__init__()
        self.instructions: dict[str, InstructionDeclaration] = {}

    def _resolve_pipeline_parts(
        self, parts: List[Union[GateCall, GatePipeByName]], seen=None
    ):
        """Helpers for resolving instruction name references inside pipelines"""

        if seen is None:
            seen = set()
        resolved: List[Union[GateCall, GatePipeByName]] = []
        for part in parts:
            if isinstance(part, str):
                if part in seen:
                    raise ValueError(f"Cyclic instruction reference detected: {part}")
                instr_decl = self.instructions.get(part)
                if instr_decl is None:
                    # Unknown name, keep as-is (or raise)
                    resolved.append(part)
                else:
                    seen.add(part)
                    # Recursively resolve the referenced pipeline's parts
                    inner_parts = self._resolve_pipeline_parts(
                        instr_decl.pipeline.parts, seen=seen
                    )
                    resolved.extend(inner_parts)
                    seen.remove(part)
            else:
                resolved.append(part)
        return resolved

    # pylint: disable=invalid-name
    def NUMBER(self, items):
        """handle number"""
        return int(str(items[0]))

    def list(self, items):
        """handle list"""
        return items

    @v_args(inline=True)
    def qubit_declaration(self, name, number):
        """handle qubit declaration"""
        return QubitDeclaration(name=name, qubit=Qubit("q", number))

    @v_args(inline=True)
    def bit_declaration(self, name, number):
        """handle qubit declaration"""
        return BitDeclaration(name=name, bit=Bit("c", number))

    @v_args(inline=True)
    def list_declaration(self, name, lst):
        """handle list declaration"""
        return ListDeclaration(name=name, items=lst)

    @v_args(inline=True)
    def instruction_declaration(self, name, gate_pip):
        """handle instruction declaration"""
        instr = InstructionDeclaration(name=name, pipeline=gate_pip)
        self.instructions[name] = instr
        return instr

    def gate_call(self, items):
        """handle gate calls"""
        name_token = items[0]
        args = []
        if len(items) > 1 and items[1] is not None:
            args = items[1]
        return GateCall(name=str(name_token), args=args)

    def args(self, items):
        """handle arguments"""
        res = []
        for it in items:
            res.append(it)
        return res

    def gate_pip(self, items):
        """handle gate pipeline"""
        parts: List[Union[GateCall, GatePipeByName]] = []
        for item in items:
            parts.append(item)
        resolved_parts = self._resolve_pipeline_parts(parts)
        return GatePipeline(parts=resolved_parts)

    @v_args(inline=True)
    def gate_pipe_by_name(self, name, rev=None):
        """handle named gate pipeline"""
        return GatePipeByName(name=name, rev=rev is not None)

    @v_args(inline=True)
    def action(self, target, count, instruction):
        """handle actions"""
        return Action(
            target=target,
            count=count,
            instruction=GatePipeline(parts=instruction.parts),
        )

    def declaration(self, items):
        """handle declarations"""
        return items[0]

    def start(self, items):
        """starting point"""
        return items

    def statement(self, items):
        """handle statements"""
        return items[0]
