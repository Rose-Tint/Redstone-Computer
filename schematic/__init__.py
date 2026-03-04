import mcschematic as mcs
from schematic.code_schem import make_code_schematic
from schematic.data_schem import make_data_schematic
# from ..cmdline import cmd, Verbosity


def make_schematics(machine_code: list[str], data: list[int], cmd):
    dir: str = cmd.schematic_dir
    prog_name: str = cmd.program_schem_name
    data_name: str = cmd.data_schem_name
    code_schem: mcs.MCSchematic = make_code_schematic(machine_code)
    code_schem.save(dir, prog_name, version=mcs.Version.JE_1_21_5)
    print(f"Instructions schematic created at {dir}/{prog_name}")
    data_schem: mcs.MCSchematic = make_data_schematic(data)
    data_schem.save(dir, data_name, version=mcs.Version.JE_1_21_5)
    print(f"Data schematic created at {dir}/{data_name}")


