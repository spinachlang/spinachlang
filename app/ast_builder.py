from app.spinach_types import (
    GatePipeline,
    GateCall,
    Action,
    QubitDeclaration,
    ListDeclaration,
    InstructionDeclaration,
)
from lark import Transformer, v_args
from typing import Union, List


class AstBuilder(Transformer):
    def name(self, items):
        return str(items[0])

    def upper_name(self, items):
        return str(items[0])

    def number(self, items):
        return int(str(items[0]))

    def list(self, items):
        return [str(i) for i in items]

    @v_args(inline=True)
    def qubit_declaration(self, name, _, number):
        return QubitDeclaration(name=name, count=number)

    @v_args(inline=True)
    def list_declaration(self, name, _, lst):
        return ListDeclaration(name=name, items=lst)

    @v_args(inline=True)
    def instruction_declaration(self, name, _, gate_pip):
        return InstructionDeclaration(name=name, pipeline=gate_pip)

    def gate_call(self, items):
        name_token = items[0]
        args = []
        if len(items) > 1 and items[1] is not None:
            args = items[1]
        return GateCall(name=str(name_token), args=args)

    def args(self, items):
        res = []
        for it in items:
            if isinstance(it, int):
                res.append(it)
            elif isinstance(it, str):
                res.append(it)
            else:
                # Should not happen
                res.append(it)
        return res

    def gate_pip(self, items):
        parts: List[Union[GateCall, str]] = []
        for it in items:
            if isinstance(it, GateCall):
                parts.append(it)
            elif isinstance(it, str):
                parts.append(it)
            else:
                parts.append(it)
        return GatePipeline(parts=parts)

    @v_args(inline=True)
    def action(self, target, _, number_opt, operation):
        if isinstance(number_opt, int):
            index = number_opt
        else:
            operation = number_opt
            index = None
        return Action(target=target, index=index, operation=operation)

    def statement(self, items):
        return items[0]
