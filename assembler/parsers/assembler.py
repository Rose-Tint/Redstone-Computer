from lark import v_args, Discard
from .. import ast
from .common import Transformer, discard
from ..opcode import Opcode



@v_args(inline=True)
class Assembler(Transformer):
    def __init__(self, macros: dict, defines: dict) -> None:
        super().__init__(visit_tokens=True)
        self.macros: dict[str, ast.Macro] = macros
        self.defines: dict[ast.Define, int] = defines
        self.labels: dict[ast.Label, int] = {}
        self.data: ast.DataSegment = []
        self.code: ast.ResolvedCode = []
        self.pc: int = 0

    @v_args(inline=False)
    def program(self, segements) -> ast.Assembly:
        # have to know address of all labels to allow forward jumping
        for stmt in self.code:
            if isinstance(stmt, ast.JumpEncoded):
                stmt.addr = self.labels[stmt.label]
        return ast.Assembly(self.data, self.code)

    @v_args(inline=False)
    def data_segment(self, datadefs: list[ast.DataDef | ast.Align]):
        for data in datadefs:
            if isinstance(data, ast.Align):
                fill = len(self.data) % data.to
                self.data.extend(fill * [0])
            elif isinstance(data, ast.DataDef):
                self.labels[data.label] = len(self.data)
                self.data.extend(data.data)
            else:
                print(f"DEBUG: skipping data {data}")
        # return Discard

    def data_def(self, label: ast.Label, data: ast.Data) -> ast.DataDef:
        return ast.DataDef(label, data)

    def align_data(self, n) -> ast.Align:
        return ast.Align(n)

    def char_data(self, ch: int) -> ast.Data:
        return [ch]

    def cstring_data(self, string: str) -> ast.Data:
        data: ast.Data = []
        for ch in string.strip('"'):
            data.append(ord(ch))
        data.append(0) # null byte
        return data

    def pstring_data(self, string: str) -> ast.Data:
        string = string.strip('"')
        data: ast.Data = [len(string)]
        for ch in string:
            data.append(ord(ch))
        return data

    def space_data(self, n: int) -> ast.Data:
        data: ast.Data = n * [0]
        return data

    def word_data(self, n: int) -> ast.Data:
        return [n]

    @v_args(inline=False)
    def code_segment(self, statements: ast.CodeSegment) -> ast.ResolvedCode:
        i: int = 0
        while i < len(statements):
            stmt = statements[i]
            if isinstance(stmt, ast.LabelDecl):
                self.labels[stmt.label] = self.pc
                i += 1
            elif isinstance(stmt, ast.MacroCall):
                macro = self.macros[stmt.name]
                expanded = ast.expand_macro(macro, stmt)
                statements.pop(i)
                for j, new_stmt in enumerate(expanded):
                    statements.insert(i + j, new_stmt)
            elif isinstance(stmt, ast.Instruction):
                self.code.append(stmt)
                self.pc += 1
                i += 1
            else:
                print(f"DEBUG: skipping `{repr(stmt)}`")
                i += 1
        return self.code

    def macro_call(self, name, *args) -> ast.MacroCall:
        return ast.MacroCall(name, [*args])

    def line(self, value, *_args):
        return value

    def no_args(self, opcode: Opcode) -> ast.Instruction:
        if opcode is Opcode.NOOP:
            return ast.RegEncoded(opcode, ast.Zero, ast.Zero, ast.Zero)
        else: # opcode is Opcode.RETURN or opcode is Opcode.EXIT
            return ast.SpecEncoded(opcode, ast.Zero, 0)

    def arith_log(self, opcode: Opcode, rd, rs, rt) -> ast.RegEncoded:
        return ast.RegEncoded(opcode, rd, rs, rt)

    def arith_i(self, opcode: Opcode, rs, rt, imm) -> ast.ImmEncoded:
        return ast.ImmEncoded(opcode, rs, rt, imm)

    def memory_ins(self, opcode: Opcode, rs, rt) -> ast.ImmEncoded:
        if opcode is Opcode.LW:
            return ast.ImmEncoded(opcode, rs, rt, 0)
        else: # opcode is Opcode.SW
            return ast.ImmEncoded(opcode, rs, rt, 0)

    def shift_cmp(self, opcode: Opcode, rs, rt) -> ast.Instruction:
        if opcode is Opcode.CMP:
            return ast.RegEncoded(opcode, rs, rt, ast.Zero)
        else:
            return ast.ImmEncoded(opcode, rs, rt, 0)

    def one_reg_imm(self, opcode: Opcode, rt, imm) -> ast.Instruction:
        if opcode is Opcode.LI or opcode is Opcode.CMPI:
            return ast.ImmEncoded(opcode, ast.Zero, rt, imm)
        else: # opcode is Opcode.RP or opcode is Opcode.WP
            return ast.SpecEncoded(opcode, rt, imm)

    def jump(self, opcode: Opcode, label) -> ast.JumpEncoded:
        return ast.JumpEncoded(opcode, label, -1)

    def push_pop(self, opcode: Opcode, reg) -> ast.SpecEncoded:
        return ast.SpecEncoded(opcode, reg, 0, 0)

    def psuedo_not(self, opcode: Opcode, rd, rs) -> ast.RegEncoded:
        return ast.RegEncoded(opcode, rs, rs, rd)

    def label_decl(self, label) -> ast.LabelDecl:
        return ast.LabelDecl(label)

    REG = ast.Register

    def OPCODE(self, name: str) -> Opcode:
        return Opcode.get(name)

    NO_ARGS_OP = OPCODE
    ARITH_LOG_OP = OPCODE
    ARITH_I_OP = OPCODE
    MEMORY_OP = OPCODE
    SHIFT_CMP_OP = OPCODE
    ONE_REG_IMM_OP = OPCODE
    PUSH_POP_OP = OPCODE
    JUMP_OP = OPCODE

    def PSUEDO_NOT_OP(self) -> Opcode:
        return Opcode.NOR

    def define(self, name: ast.Define) -> int:
        return self.defines[name]

    def named_imm(self, name) -> int:
        return self.labels[name]

    def DEFINE(self, *toks) -> ast.Define:
        return ast.Define("".join(toks))

    def LABEL(self, label) -> ast.Label:
        return ast.Label(str(label))

    def macro_params(self, *params) -> list[ast.MacroParam]:
        return [*params]

    def MACRO_PARAM(self, *toks) -> ast.MacroParam:
        return ast.MacroParam("".join(toks))

    def STRING(self, s) -> str:
        return s.strip('"')

    def CHAR(self, ch: str) -> int:
        ch = ch.strip("'")
        return ord(ch)

    def ESCAPE_CHAR(self, ch):
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
    WS = discard
    WS_INLINE = discard
    code__NEWLINE = discard
    NEWLINE = discard
