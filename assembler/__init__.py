import sys
from typing import TextIO, Callable
from dataclasses import dataclass, field
from .parsers import parse_file
from .parsers.assembler import Assembler
from .parsers.importer import Importer
from .parsers.preprocessor import Preprocessor, Preprocessed
from . import ast

class Program:
    def __init__(self, fpath: str, asm: ast.Assembly):
        self.filepath: str = fpath
        self.code: ast.ResolvedCode = asm.code_segment
        self.data: ast.DataSegment = asm.data_segment

    def machine_code_str(self) -> list[str]:
        return [ins.machine_code_str() for ins in self.code]

    def byte_code(self) -> bytearray:
        arr = bytearray(2 * len(self.code))
        for ins in self.code:
            mcode: int = ins.machine_code()
            arr.append((mcode >> 8) << 8) # top half
            arr.append((mcode << 8) >> 8) # bottom half
        return arr

def assemble(filepath: str) -> Program:
    start_tree = parse_file(filepath)
    full_tree = Importer(filepath).visit(start_tree)
    prepped: Preprocessed = Preprocessor().transform(full_tree)
    asm: ast.Assembly = Assembler(prepped.defines).transform(prepped.tree)
    return Program(filepath, asm)
