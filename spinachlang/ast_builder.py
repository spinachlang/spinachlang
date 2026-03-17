"""Abstract syntax tree builder"""

from typing import Union, List
from pytket import Qubit, Bit
from lark import Transformer, v_args

from .spinach_types import (
    GatePipeByName,
    GatePipeline,
    GateCall,
    Action,
    ConditionalAction,
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
        """handle number — returns int for plain integers, float for decimals.

        NOTE: Lark calls terminal callbacks with the Token directly (not wrapped
        in a list), so we must use str(items), not str(items[0]).  The original
        int(str(items[0])) took only the first *character*, which happened to
        work for single-digit indices but would silently truncate '42' to 4.
        """
        s = str(items)
        return float(s) if "." in s else int(s)

    @v_args(inline=True)
    def qubit_ref(self, number):
        """Handle explicit 'q N' qubit index syntax.

        q 0, q 1, q 2 … are exactly equivalent to the bare integers 0, 1, 2
        as qubit references.  They can appear in:
          - action targets:        q 0 -> H
          - gate arguments:        target -> CX(q 1)
          - list elements:         [q 0, q 1] -> H
          - conditional targets:   q 0 -> X if flag

        The number must be a non-negative integer (not a float angle).
        """
        if not isinstance(number, int):
            raise ValueError(
                f"Qubit index in 'q N' syntax must be a non-negative integer, got {number!r}. "
                "Use bare numbers for gate angles, e.g. RZ(0.5)."
            )
        return number

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

    def cond_pip(self, items):
        """Handle a conditional branch pipeline.

        Returns a GatePipeline regardless of whether the source was a single
        gate, a named instruction, or a parenthesised multi-gate pipeline.
        """
        item = items[0]
        if isinstance(item, GateCall):
            return GatePipeline(parts=[item])
        if isinstance(item, GatePipeByName):
            return GatePipeline(parts=[item])
        # Already a GatePipeline coming from "(" gate_pip ")"
        return item

    def conditional_action(self, items):
        """Handle classically conditional actions.

        Two forms (both with _IF_KW and _ELSE_KW filtered out):
          if-only:   [target, if_pipeline, bit_name]          (3 items)
          if/else:   [target, if_pipeline, bit_name, else_pipeline]  (4 items)
        """
        target = items[0]
        if_pipeline = items[1]   # GatePipeline from cond_pip
        condition_bit = str(items[2])  # NAME token → condition bit name
        else_pipeline = items[3] if len(items) > 3 else None
        return ConditionalAction(
            target=target,
            condition_bit=condition_bit,
            if_pipeline=if_pipeline,
            else_pipeline=else_pipeline,
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
