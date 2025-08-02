from app.frontend.spinach_front import SpinachFront
from app.backend.spinach_back import SpinachBack
from app.ast_builder import AstBuilder


class Spinach:

    @staticmethod
    def creat_circuit(code: str):
        return SpinachBack.compile_into_circuit(AstBuilder.transform(SpinachFront.get_tree(code)))


if __name__ == '__init__':
