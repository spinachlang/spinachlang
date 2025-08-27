"""frontend of spinach"""

from pathlib import Path
from lark import Lark


class SpinachFront:  # pylint: disable=too-few-public-methods
    """frontend of spinach"""

    @staticmethod
    def get_tree(code: str):
        """generate tree out of spinach code"""
        with open(Path("app") / "frontend" / "grammar.lark", encoding="utf-8") as f:
            grammar = f.read()
        parser = Lark(grammar, start="start", parser="lalr")
        return parser.parse(code)
