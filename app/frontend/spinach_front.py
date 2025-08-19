from lark import Lark
from pathlib import Path


class SpinachFront:
    @staticmethod
    def get_tree(code: str):
        with open(Path("app") / "frontend" / "grammar.lark") as f:
            grammar = f.read()
        parser = Lark(grammar, start="start", parser="earley")
        return parser.parse(code)
