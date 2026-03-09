import sys
from assembler import assemble
from simulator import Simulator


def main(argv: list[str]) -> None:
    sim = Simulator()
    if len(argv) > 1:
        print(f"Running Simulator with {argv[1]} loaded")
        sim.run(argv[1])
    else:
        print(f"Running Simulator")
        sim.run()

if __name__ == "__main__":
    main(sys.argv)
