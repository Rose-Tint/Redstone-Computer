import sys
from assembler import assemble
from simulator import run_simulator


def main(argv: list[str]) -> None:
    if len(argv) > 1:
        print(f"Running Simulator with {argv[1]} loaded")
        run_simulator(argv[1], assemble(argv[1]))

if __name__ == "__main__":
    main(sys.argv)
