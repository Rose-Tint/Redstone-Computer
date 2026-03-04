import argparse as ap


cmd_parser: ap.ArgumentParser = ap.ArgumentParser(
    description="Parse assembly files into WorldEdit schematics"
)
cmd_parser.add_argument(
    "program_name", metavar="program-name",
    help="Name of the program being assembled"
    )
cmd_parser.add_argument(
    "-asm", dest="asm_filename",
    help="Name of the assembly file"
    )
cmd_parser.add_argument(
    "-S", "--source-dir", default="./",
    help="Directory where the source files (.asm) can be found"
    )
cmd_parser.add_argument(
    "--dump-mc", nargs='?', const=True, default=False,
    help="Generates a .mc file in the given folder, or in `--source-dir` if not specified"
)
cmd_parser.add_argument(
    "--no-schematic", action="store_true", default=False,
    help="Disable making the schematic"
    )
cmd_parser.add_argument(
    "--schematic-dir",
    help="Directory where to put the schematic file"
    )
cmd_parser.add_argument(
    "--program-schematic-name",
    help="Full name of the schematic; defaults to \"<program-name>_PROGRAM\""
    )
cmd_parser.add_argument(
    "--data-schematic-name",
    help="Full name of the schematic; defaults to \"<program-name>_DATA\""
    )
cmd_parser.add_argument(
    "--simulate", "--sim", action="store_true", default=False,
    help="Enable the simulator (disables schematics)"
    )


