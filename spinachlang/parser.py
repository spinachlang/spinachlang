"""frontend of spinach"""

from pathlib import Path
from lark import Lark


class Parser:  # pylint: disable=too-few-public-methods
    """frontend of spinach"""

    @staticmethod
    def get_tree(code: str):
        """generate tree out of spinach code"""

        script_dir = Path(__file__).resolve().parent
        grammar_path = script_dir / "grammar.lark"

        with open(grammar_path, encoding="utf-8") as f:
            grammar = f.read()
        parser = Lark(grammar, start="start", parser="lalr")
        return parser.parse(code)
