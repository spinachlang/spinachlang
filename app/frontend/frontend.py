from lark import Lark, Transformer, v_args

with open("grammar.lark") as f:
    grammar = f.read()

parser = Lark(grammar, start="start", parser="lalr")  # or parser="earley" if you prefer


class TreeToAST(Transformer):
    def number(self, items):
        return int(items[0])

    def name(self, items):
        return str(items[0])

    def upper_name(self, items):
        return str(items[0])


# Example usage
def parse_code(code):
    tree = parser.parse(code)
    return TreeToAST().transform(tree)


if __name__ == "__main__":
    program = """
allo: 0
tom: 1
tarte: 2
lol: 3
list: [allo, tom]
instructions: N | H | N(lol, tom)
instructions2: N | H | N(ok, mama)
list -> instructions
allo -> 3 H | I
    """
    ast = parse_code(program)
    print(ast.pretty())
