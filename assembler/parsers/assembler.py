from lark import v_args, Discard, Token
from .. import ast
from .common import Transformer, discard
from ..opcode import Opcode
from ..ast.meta import Meta, Located



@v_args(inline=True)
class Assembler(Transformer):
    def __init__(self, defines: dict) -> None:
        super().__init__(visit_tokens=True)
        self.macros: dict[str, ast.Macro] = {}
        self.defines: dict[str, ast.Define] = defines
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

    def data_def(self, label: ast.Label, data: ast.Data) -> ast.DataDef:
        return ast.DataDef(label._meta, label, data)

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

    def macro_statement(self, stmt) -> ast.MacroStatement:
        return stmt

    def macro_def(self, name: ast.Label, params, *body):
        self.macros[str(name)] = ast.Macro(name._meta, name.name, params, [*body])
        return Discard

    def macro_call(self, name: ast.Label, *args) -> ast.MacroCall:
        return ast.MacroCall(name._meta, name.name, [*args])

    def line(self, value, *_args):
        return value

    def no_args(self, loc_op: Located[Opcode]) -> ast.Instruction:
        meta, opcode = loc_op.meta, loc_op.data
        if opcode is Opcode.NOOP:
            return ast.RegEncoded(meta, opcode, ast.Zero, ast.Zero, ast.Zero)
        else: # opcode is Opcode.RETURN or opcode is Opcode.EXIT
            return ast.SpecEncoded(meta, opcode, ast.Zero, 0)

    def arith_log(self, loc_op: Located[Opcode], rd, rs, rt) -> ast.RegEncoded:
        meta, opcode = loc_op.meta, loc_op.data
        return ast.RegEncoded(meta, opcode, rs, rt, rd)

    def arith_i(self, loc_op: Located[Opcode], rs, rt, imm) -> ast.ImmEncoded:
        meta, opcode = loc_op.meta, loc_op.data
        return ast.ImmEncoded(meta, opcode, rs, rt, imm)

    def memory_ins(self, loc_op: Located[Opcode], rs, rt) -> ast.ImmEncoded:
        meta, opcode = loc_op.meta, loc_op.data
        if opcode is Opcode.LW:
            return ast.ImmEncoded(meta, opcode, rs, rt, 0)
        else: # opcode is Opcode.SW
            return ast.ImmEncoded(meta, opcode, rs, rt, 0)

    def shift_cmp(self, loc_op: Located[Opcode], rs, rt) -> ast.Instruction:
        meta, opcode = loc_op.meta, loc_op.data
        if opcode is Opcode.CMP:
            return ast.RegEncoded(meta, opcode, rs, rt, ast.Zero)
        else:
            return ast.ImmEncoded(meta, opcode, rs, rt, 0)

    def one_reg_imm(self, loc_op: Located[Opcode], rt, imm) -> ast.Instruction:
        meta, opcode = loc_op.meta, loc_op.data
        if opcode is Opcode.LI:
            return ast.ImmEncoded(meta, opcode, ast.Zero, rt, imm)
        elif opcode is Opcode.CMPI:
            return ast.ImmEncoded(meta, opcode, rt, ast.Zero, imm)
        else: # opcode is Opcode.RP or opcode is Opcode.WP
            return ast.SpecEncoded(meta, opcode, rt, imm)

    def jump(self, loc_op: Located[Opcode], label) -> ast.JumpEncoded:
        meta, opcode = loc_op.meta, loc_op.data
        return ast.JumpEncoded(meta, opcode, label, -1)

    def push_pop(self, loc_op: Located[Opcode], reg) -> ast.SpecEncoded:
        meta, opcode = loc_op.meta, loc_op.data
        return ast.SpecEncoded(meta, opcode, reg, 0, 0)

    def psuedo_not(self, loc_op: Located[Opcode], rd, rs) -> ast.RegEncoded:
        meta, opcode = loc_op.meta, loc_op.data
        return ast.RegEncoded(meta, opcode, rs, rs, rd)

    def label_decl(self, label) -> ast.LabelDecl:
        return ast.LabelDecl(label)

    def REG(self, tok) -> ast.Register:
        return ast.Register(tok, Meta.from_token(tok))

    def OPCODE(self, name: Token) -> Located[Opcode]:
        return Located(Meta.from_token(name), Opcode.get(name))

    NO_ARGS_OP = OPCODE
    ARITH_LOG_OP = OPCODE
    ARITH_I_OP = OPCODE
    MEMORY_OP = OPCODE
    SHIFT_CMP_OP = OPCODE
    ONE_REG_IMM_OP = OPCODE
    PUSH_POP_OP = OPCODE
    JUMP_OP = OPCODE

    def PSUEDO_NOT_OP(self, tok: Token) -> Located[Opcode]:
        meta = Meta.from_token(tok)
        return Located(meta, Opcode.NOR)

    # def define(self, name: ast.Define) -> int:
    #     return self.defines[name]

    def named_imm(self, name) -> int:
        return self.labels[name]

    def DEFINE(self, *toks: Token) -> ast.Define:
        meta = Meta.from_token(toks[0])
        name = "".join(toks)
        return ast.Define(meta, name, self.defines[name].value)

    def LABEL(self, label: Token) -> ast.Label:
        return ast.Label(Meta.from_token(label), str(label))

    def macro_params(self, *params) -> list[ast.MacroParam]:
        return [*params]

    # def MACRO_PARAM(self, *toks) -> ast.MacroParam:
    #     return ast.MacroParam("".join(toks))

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
