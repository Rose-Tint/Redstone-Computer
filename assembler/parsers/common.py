from lark import Lark, Tree, Discard, Token
import lark
from lark.exceptions import UnexpectedInput, UnexpectedToken, UnexpectedEOF


_GRAMMAR_PATH = "assembler/grammar/program.lark"
_parser = Lark.open(
    _GRAMMAR_PATH,
    start="program",
    import_paths=["assembler/grammar"],
    source_path="assembler/grammar"
    )

# class ParseError(lark.ParseError): pass

def discard(*args, **kwargs):
    return Discard

def parse_file(path: str) -> Tree:
    with open(path, "r") as file:
        contents = file.read()
        try:
            tree = _parser.parse(contents)
            return tree
        except UnexpectedInput as err:
            ln, col = err.line, err.column
            print(f"Unexpected input in {path} at line {ln}, col {col}")
            context = err.get_context(contents).replace("\n", "\n\t")
            print(f"\t{context}")
            err.__traceback__ = None
            raise err

class Visitor(lark.Visitor):
    def _call_userfunc(self, tree: Tree):
        new_tree = tree.copy()
        new_tree.data = tree.data.rpartition("__")[-1]
        return super()._call_userfunc(new_tree)

class Transformer(lark.Transformer):
    def _call_userfunc(self, tree: Tree, new_children=None):
        new_tree = tree.copy()
        new_tree.data = tree.data.rpartition("__")[-1]
        return super()._call_userfunc(new_tree, new_children)

    def _call_userfunc_token(self, token: Token):
        token.type = token.type.rpartition("__")[-1]
        return super()._call_userfunc_token(token)
