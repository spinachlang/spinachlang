"""The spinach language"""

from .parser import Parser
from .backend import Backend
from .ast_builder import AstBuilder


class Spinach:
    """The spinach language"""

    @staticmethod
    def create_circuit(code: str):
        """generate a tket circuit from spinach code"""
        built = AstBuilder().transform(Parser.get_tree(code))
        return Backend.compile_to_circuit(built)

    @staticmethod
    def compile(code: str, language: str) -> str:
        """translate spinach code to other languages"""
        dispatch = {
            "qasm": Backend.compile_to_openqasm,
            "json": Backend.compile_to_json,
            "cirq": Backend.compile_to_cirq_python,
            "quil": Backend.compile_to_quil,
        }
        if language not in dispatch:
            raise ValueError("language cant be none")
        fn = dispatch.get(language)
        return fn(Spinach.create_circuit(code=code))
