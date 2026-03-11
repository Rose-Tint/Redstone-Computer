from dataclasses import dataclass
from .parsers import parse_file
from .parsers.assembler import Assembler
from .parsers.importer import Importer
from .parsers.preprocessor import Preprocessor, Preprocessed
from . import ast

#
@dataclass
class Program:
    filepath: str
    code: ast.ResolvedCode
    machine_code: list[str]
    data: list[int]

# TODO: add binary option
def assemble(filepath: str) -> Program:
    start_tree = parse_file(filepath)
    full_tree = Importer(filepath).visit(start_tree)
    prepped: Preprocessed = Preprocessor().transform(full_tree)
    assembly: ast.Assembly = Assembler(prepped.defines).transform(prepped.tree)
    mcode = [ins.machine_code_str() for ins in assembly.code_segment]
    data = assembly.data_segment
    return Program(filepath, assembly.code_segment, mcode, data)
