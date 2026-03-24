import warnings
from typing import Callable
from lark import v_args, Discard, Token
from .. import ast
from .common import Transformer, discard
from ..ast.opcode import Opcode, OpcodeEnum
from ..ast.meta import Meta, Located


@v_args(inline=True)
class Assembler(Transformer):
    def __init__(self, defines: dict) -> None:
        super().__init__(visit_tokens=True)
        self.macros: dict[ast.Name, ast.Macro] = {}
        self.defines: dict[str, ast.Define] = defines
        self.labels: dict[ast.Name, int] = {}
        self.data: ast.DataSegment = []
        self.code: ast.ResolvedCode = []
        self.pc: int = 0

    @v_args(inline=False)
    def program(self, segements) -> ast.Assembly:
        # have to know address of all labels to allow forward jumping
        for stmt in self.code:
            if isinstance(stmt, ast.JumpEncoded):
                stmt.addr = self.labels[stmt.label]
        labels: set[ast.Label] = {
            ast.Label.from_name(name, value) for (name, value) in self.labels.items()
        }
        return ast.Assembly(
            data_segment = self.data,
            code_segment = self.code,
            # labels = labels,
            # defines = set(self.defines.values()),
            # macros = set(self.macros.values())
            )

    @v_args(inline=False)
    def data_segment(self, datadefs: list[ast.DataDef | ast.Align]):
        for data in datadefs:
            if isinstance(data, ast.Align):
                fill = len(self.data) % data.to
                self.data.extend(fill * [0])
            elif isinstance(data, ast.DataDef):
                self.labels[data.name] = len(self.data)
                self.data.extend(data.data)
            else:
                warnings.warn(f"skipping data {data}", RuntimeWarning)

    def data_def(self, name: ast.Name, data: ast.Data) -> ast.DataDef:
        return ast.DataDef(name, data)

    @v_args(inline=False)
    def code_segment(self, statements: ast.CodeSegment) -> ast.ResolvedCode:
        i: int = 0
        while i < len(statements):
            stmt = statements[i]
            if isinstance(stmt, ast.LabelDecl):
                self.labels[stmt.label] = self.pc
                i += 1
            elif isinstance(stmt, ast.MacroCall):
                macro: ast.Macro = self.macros[stmt.name]
                expanded: ast.CodeSegment = ast.expand_macro(macro, stmt)
                statements.pop(i)
                for j, new_stmt in enumerate(expanded):
                    statements.insert(i + j, new_stmt)
            elif isinstance(stmt, ast.Instruction):
                self.code.append(stmt)
                self.pc += 1
                i += 1
            else:
                warnings.warn(f"skipping statement: `{repr(stmt)}`", RuntimeWarning)
                i += 1
        return self.code

    def macro_def(self, name: ast.Name, params, *body):
        self.macros[name] = ast.Macro(name, params, [*body])
        return Discard

    def macro_call(self, name: ast.Name, *args) -> ast.MacroCall:
        return ast.MacroCall(name, [*args])

    def no_args(self, opcode: Opcode) -> ast.Instruction:
        if opcode == OpcodeEnum.NOOP:
            return ast.RegEncoded(opcode, ast.Zero, ast.Zero, ast.Zero)
        else: # opcode is Opcode.RETURN or opcode is Opcode.EXIT
            return ast.SpecEncoded(opcode, ast.Zero, 0, 0)

    def arith_log(self, opcode: Opcode, rd, rs, rt) -> ast.RegEncoded:
        return ast.RegEncoded(opcode, rs, rt, rd)

    def arith_i(self, opcode: Opcode, rs, rt, imm) -> ast.ImmEncoded:
        return ast.ImmEncoded(opcode, rs, rt, imm)

    def memory_ins(self, opcode: Opcode, rs, rt) -> ast.ImmEncoded:
        if opcode == OpcodeEnum.LW:
            return ast.ImmEncoded(opcode, rs, rt, 0)
        else: # opcode is Opcode.SW
            return ast.ImmEncoded(opcode, rs, rt, 0)

    def shift_cmp(self, opcode: Opcode, rs, rt) -> ast.Instruction:
        if opcode == OpcodeEnum.CMP:
            return ast.RegEncoded(opcode, rs, rt, ast.Zero)
        elif opcode == OpcodeEnum.NOT:
            return ast.RegEncoded(opcode, rt, rt, rs)
        else:
            return ast.ImmEncoded(opcode, rs, rt, 0)

    def one_reg_imm(self, opcode: Opcode, rt, imm) -> ast.Instruction:
        if opcode == OpcodeEnum.LI:
            return ast.ImmEncoded(opcode, ast.Zero, rt, imm)
        elif opcode == OpcodeEnum.CMPI:
            return ast.ImmEncoded(opcode, rt, ast.Zero, imm)
        else: # opcode is Opcode.RP or opcode is Opcode.WP
            return ast.SpecEncoded(opcode, rt, imm, 0)

    def jump(self, opcode: Opcode, label) -> ast.JumpEncoded:
        return ast.JumpEncoded(opcode, label, -1)

    def push_pop(self, opcode: Opcode, reg) -> ast.SpecEncoded:
        return ast.SpecEncoded(opcode, reg, 0, 0)

    def label_decl(self, label) -> ast.LabelDecl:
        return ast.LabelDecl(label)

    def OPCODE(self, name: Token) -> Opcode:
        return Opcode(str(name), Meta.from_lark(name))

    NO_ARGS_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    ARITH_LOG_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    ARITH_I_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    MEMORY_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    SHIFT_CMP_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    ONE_REG_IMM_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    PUSH_POP_OP: Callable[["Assembler", Token], Opcode] = OPCODE
    JUMP_OP: Callable[["Assembler", Token], Opcode] = OPCODE

    def named_imm(self, name) -> int:
        return self.labels[name]

    def DEFINE(self, token: Token) -> ast.Define:
        return self.defines[str(token)] @ token

    def LABEL(self, label_tok: Token) -> ast.Label:
        return ast.Label(label_tok)

    @v_args(inline=False)
    def macro_params(self, params) -> list[ast.MacroParam]:
        return params

    INT = int
    WS = discard
    WS_INLINE = discard
    code__NEWLINE = discard
    NEWLINE = discard
