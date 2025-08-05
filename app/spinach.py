from app.frontend.spinach_front import SpinachFront
from app.backend.spinach_back import SpinachBack
from app.ast_builder import AstBuilder


class Spinach:
    @staticmethod
    def creat_circuit(code: str):
        return SpinachBack.compile_to_circuit(
            AstBuilder().transform(SpinachFront.get_tree(code))
        )

    @staticmethod
    def compile(code: str, language: str) -> str:
        dispatch = {
            "qasm": SpinachBack.compile_to_openqasm,
            "qiskit": SpinachBack.compile_to_qiskit,
            "pyquil": SpinachBack.compile_to_pyquil,
            "cirq": SpinachBack.compile_to_cirq,
        }
        if language not in dispatch:
            raise ValueError("language cant be none")
        fn = dispatch.get(language)
        return fn(Spinach.creat_circuit(code=code))
