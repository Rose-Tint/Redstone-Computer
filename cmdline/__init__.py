import sys
# import argparse as ap
from typing import Optional
from .parser import cmd_parser


MCE_SCHEMATICS_FOLDER: str = "C:/Users/12624/AppData/Roaming/ModrinthApp/profiles/WorldEdit/config/worldedit/schematics"


class Cmdline:
    def __init__(self, args: list[str] = sys.argv[1:]):
        cmd = cmd_parser.parse_args()
        self.program_name: str = cmd.program_name
        self.asm_filename: str = cmd.asm_filename or self.program_name + ".asm"
        self.source_dir: str = cmd.source_dir
        self.mc_dir: Optional[str] = None if cmd.dump_mc is False else self.source_dir if cmd.dump_mc is True else cmd.dump_mc
        self.make_schematic: bool = not cmd.no_schematic
        self.schematic_dir: str = cmd.schematic_dir or MCE_SCHEMATICS_FOLDER
        self.program_schem_name: str = cmd.program_schematic_name or f"{self.program_name}_PROGRAM"
        self.data_schem_name: str = cmd.data_schematic_name or f"{self.program_name}_DATA"
        self.simulate: bool = cmd.simulate or False

    @property
    def assembly_filepath(self) -> str:
        return f"{self.source_dir}/{self.asm_filename}"

    @property
    def machine_code_dump_path(self) -> Optional[str]:
        if self.mc_dir is None:
            return None
        else:
            return f"{self.mc_dir}/{self.program_name}.mc"

    @property
    def data_dump_path(self) -> Optional[str]:
        if self.mc_dir is None:
            return None
        else:
            return f"{self.mc_dir}/{self.program_name}.data"

    def help(self):
        cmd_parser.print_help()
        exit()

cmd: Cmdline = Cmdline(sys.argv)
