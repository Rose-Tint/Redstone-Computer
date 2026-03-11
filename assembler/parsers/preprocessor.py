from dataclasses import dataclass
from lark import v_args, Discard, Tree, Token
from .common import Transformer, discard
from .. import ast
from ..ast import Meta

@dataclass
class Preprocessed:
    tree: Tree
    defines: dict[str, ast.Define]

@v_args(inline=True)
class Preprocessor(Transformer):
    def __init__(self) -> None:
        super().__init__(visit_tokens=True)
        self.defines: dict[str, ast.Define] = {}

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
        return Preprocessed(tree, self.defines)

    def definition(self, name: Token, value: int):
        meta = Meta.from_token(name)
        define = ast.Define(meta, str(name), value)
        self.defines[name] = define
        return Discard

    def MACRO_PARAM(self, *toks: Token) -> ast.MacroParam:
        meta = Meta.from_token(toks[0])
        return ast.MacroParam(meta, "".join(toks))

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
