from dataclasses import dataclass
from lark import v_args, Discard, Tree
from .common import Transformer, discard
from .. import ast

@dataclass
class Preprocessed:
    tree: Tree
    defines: dict[ast.Define, int]
    macros: dict[str, ast.Macro]

@v_args(inline=True)
class Preprocessor(Transformer):
    def __init__(self, path: str) -> None:
        super().__init__(visit_tokens=True)
        self.defines: dict = {}
        self.macros: dict = {}

    @v_args(tree=True)
    def program(self, tree: Tree) -> Preprocessed:
        # merges imported data segments to allow 'undeclared' data labels
        data_segment = None
        i: int = 0
        while i < len(tree.children):
            child = tree.children[i]
            if child.data == "data_segment":
                if data_segment is None:
                    data_segment = child
                else:
                    data_segment.children += child.children
                    tree.children.pop(i)
                    continue
            # ensures all macros are processed first by the assembler
            if child.data == "macro_def":
                tree.children.remove(child)
                tree.children.insert(0, child)
            i += 1
        return Preprocessed(tree, self.defines, self.macros)

    def definition(self, name, value):
        self.defines[name] = value
        return Discard

    def MACRO_PARAM(self, *toks) -> ast.MacroParam:
        return ast.MacroParam("".join(toks))

    def STRING(self, s) -> str:
        return s.strip('"')

    def CHAR(self, ch: str) -> int:
        ch = ch.strip("'")
        return ord(ch)

    INT = int

    text_segment = discard
    WS = discard
    WS_INLINE = discard
    NEWLINE = discard