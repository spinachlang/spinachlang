"""frontend of spinach"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from lark import Lark


@lru_cache(maxsize=1)
def _build_parser() -> Lark:

    grammar_path = Path(__file__).resolve().parent / "grammar.lark"
    try:
        grammar = grammar_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Spinach grammar file not found: {grammar_path}"
        ) from None
    except PermissionError:
        raise PermissionError(
            f"Permission denied reading grammar file: {grammar_path}"
        ) from None
    return Lark(grammar, start="start", parser="lalr")


class Parser:  # pylint: disable=too-few-public-methods
    """Frontend wrapper that exposes a single entry point for parsing Spinach source code."""

    @staticmethod
    def get_tree(code: str):
        """Parse *code* and return the Lark parse tree.

        The underlying Lark parser is built once per process (cached via
        ``_build_parser``) so repeated calls incur only the parse cost.
        """
        return _build_parser().parse(code)
