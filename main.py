import sys
from assembler import Program, assemble
from schematic import make_schematics
from simulator import run_simulator
from cmdline import *


if __name__ == "__main__":
    if len(sys.argv) < 2:
        cmd.help()
    else:
        program: Program = assemble(cmd.assembly_filepath)
        machine_code: list[str] = program.machine_code
        data: list[int] = program.data
        if cmd.machine_code_dump_path is not None:
            with open(cmd.machine_code_dump_path, 'w') as mc_file:
                mc_file.write("\n".join(machine_code) + "\n")
        if cmd.data_dump_path is not None:
            with open(cmd.data_dump_path, 'w') as data_file:
                data_strs = [str(d) for d in data]
                data_file.write("\n".join(data_strs) + "\n")
        if cmd.simulate:
            run_simulator(cmd.assembly_filepath, program)
        elif cmd.make_schematic is True:
            make_schematics(machine_code, data, cmd)
