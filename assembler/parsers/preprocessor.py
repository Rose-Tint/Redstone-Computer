from utils import T
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
        define = ast.Define(name, value)
        self.defines[name] = define
        return Discard

    def align_data(self, n) -> ast.Align:
        return ast.Align(n)

    def data_char_type(self, ch: int) -> ast.Data:
        return [ch]

    def data_cstring_type(self, string: str) -> ast.Data:
        data: ast.Data = []
        for ch in string.strip('"'):
            data.append(ord(ch))
        data.append(0) # null byte
        return data

    def data_pstring_type(self, string: str) -> ast.Data:
        string = string.strip('"')
        data: ast.Data = [len(string)]
        for ch in string:
            data.append(ord(ch))
        return data

    def data_space_type(self, n: int) -> ast.Data:
        data: ast.Data = n * [0]
        return data

    def data_word_type(self, n: int) -> ast.Data:
        return [n]

    @v_args(inline=False)
    def lines(self, body: list[T]) -> list[T]:
        return body

    def REG(self, tok) -> ast.Register:
        return ast.Register(tok, Meta.from_lark(tok))

    def MACRO_PARAM(self, token: Token) -> ast.MacroParam:
        return ast.MacroParam(token)

    def STRING(self, s) -> str:
        return s.strip('"')

    def CHAR(self, ch: str) -> int:
        ch = ch.strip("'")
        return ord(ch)

    def ESCAPE_CHAR(self, ch: str) -> str:
        match ch:
            case "\\a": return "\a"
            case "\\b": return "\b"
            case "\\f": return "\f"
            case "\\n": return "\n"
            case "\\r": return "\r"
            case "\\t": return "\t"
            case "\\v": return "\v"
            case "\\0": return "\0"
            case "\\'": return "\'"
            case '\\"': return "\""
            case _: return ch

    INT = int

    text_segment = discard
    WS = discard
    WS_INLINE = discard
    NEWLINE = discard
