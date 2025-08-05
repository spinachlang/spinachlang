from app.spinach_types import (
    GatePipeline,
    GateCall,
    Action,
    QubitDeclaration,
    ListDeclaration,
    InstructionDeclaration,
)
from lark import Transformer, v_args
from typing import Union, List, Any


class AstBuilder(Transformer):
    def __init__(self):
        super().__init__()
        self.instructions: dict[str, InstructionDeclaration] = {}

    # Helpers for resolving instruction name references inside pipelines
    def _resolve_pipeline_parts(
        self, parts: List[Union[GateCall, str, Any]], seen=None
    ):
        if seen is None:
            seen = set()
        resolved: List[Union[GateCall, Any]] = []
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

    def name(self, items):
        return str(items[0])

    def upper_name(self, items):
        return str(items[0])

    def number(self, items):
        return int(str(items[0]))

    def list(self, items):
        return [str(i) for i in items]

    @v_args(inline=True)
    def qubit_declaration(self, name, number):
        return QubitDeclaration(name=name, number=number)

    @v_args(inline=True)
    def list_declaration(self, name, lst):
        return ListDeclaration(name=name, items=lst)

    @v_args(inline=True)
    def instruction_declaration(self, name, gate_pip):
        instr = InstructionDeclaration(name=name, pipeline=gate_pip)
        self.instructions[name] = instr
        return instr

    def gate_call(self, items):
        name_token = items[0]
        args = []
        if len(items) > 1 and items[1] is not None:
            args = items[1]
        return GateCall(name=str(name_token), args=args)

    def args(self, items):
        res = []
        for it in items:
            if isinstance(it, (int, str)):
                res.append(it)
            else:
                res.append(it)
        return res

    def gate_pip(self, items):
        # items may include GateCall and/or instruction names (str)
        parts: List[Union[GateCall, str, Any]] = []
        for it in items:
            parts.append(it)
        # Resolve any nested instruction name references inside this pipeline
        resolved_parts = self._resolve_pipeline_parts(parts)
        return GatePipeline(parts=resolved_parts)

    @v_args(inline=True)
    def action(self, target, count, instruction):
        # instruction might be a string name, a GatePipeline, or mix
        if isinstance(instruction, str):
            instr_decl = self.instructions.get(instruction)
            if instr_decl is None:
                raise ValueError(
                    f"Unknown instruction referenced in action: {instruction}"
                )
            pipeline = instr_decl.pipeline
        elif isinstance(instruction, GatePipeline):
            # Resolve any embedded name references inside the pipeline parts
            resolved_parts = self._resolve_pipeline_parts(instruction.parts)
            pipeline = GatePipeline(parts=resolved_parts)
        else:
            pipeline = instruction  # fallback; could be invalid shape
        return Action(target=target, count=count, instruction=pipeline)

    def declaration(self, items):
        # unwrap single declaration
        return items[0]

    def start(self, items):
        # top-level program: list of declarations/actions
        return items

    def statement(self, items):
        return items[0]
