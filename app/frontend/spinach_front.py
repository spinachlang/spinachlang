from lark import Lark


class SpinachFront:
    @staticmethod
    def get_tree(code: str):
        with open("grammar.lark") as f:
            grammar = f.read()
        parser = Lark(grammar, start="start", parser="lalr")
        return parser.parse(code)
