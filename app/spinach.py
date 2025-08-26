"""The spinach language"""

from app.frontend.spinach_front import SpinachFront
from app.backend.spinach_back import SpinachBack
from app.ast_builder import AstBuilder


class Spinach:
    """The spinach language"""

    @staticmethod
    def creat_circuit(code: str):
        """generate a tket circuit from spinach code"""
        built = AstBuilder().transform(SpinachFront.get_tree(code))
        return SpinachBack.compile_to_circuit(built)

    @staticmethod
    def compile(code: str, language: str) -> str:
        """translate spinach code to other languages"""
        dispatch = {
            "qasm": SpinachBack.compile_to_openqasm,
            "json": SpinachBack.compile_to_json,
            "cirq": SpinachBack.compile_to_cirq_python,
            "quil": SpinachBack.compile_to_quil,
        }
        if language not in dispatch:
            raise ValueError("language cant be none")
        fn = dispatch.get(language)
        return fn(Spinach.creat_circuit(code=code))
