from ast import Dict
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from lark import Lark, Transformer, v_args, Tree, Tokenclass
from app.types import *
from app.types import QubitDeclaration
from app.types import Action
from pytket import Circuit


class SpinachBack:
    @staticmethod
    def __get_max_qubit_number(ast_nodes):
        return max(
            (decl.number for decl in ast_nodes if isinstance(decl, QubitDeclaration)),
            default=0,
        )
    @staticmethod
    def __handle_action(action: Action, c: Circuit, qubits: Dict, lists: Dict, instructions: Dict):



    @staticmethod
    def compile_into_circuit(ast_nodes):
        c = Circuit(SpinachBack.__get_max_qubit_number(ast_nodes))
        qubit_dict = dict()
        list_dict = dict()
        instruction_dict = dict()
        for node in ast_nodes:
            if isinstance(node, QubitDeclaration):
                qubit_dict[node.name] = node.number
            elif isinstance(node, ListDeclaration):
                list_dict[node.name] = node.items
            elif isinstance(node, InstructionDeclaration):
                instruction_dict[node.name] = node.pipline
            elif isinstance(node, Action):
                SpinachBack.__handle_action(node, c, qubit_dict, list_dict, instruction_dict)
        return c
