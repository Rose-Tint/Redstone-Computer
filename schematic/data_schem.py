import mcschematic as mcs
from dataclasses import dataclass
from .position import *


@dataclass
class DataBlock:
    start_addr: int
    item1: int
    item2: int
    item3: int
    item4: int


ROW_COUNT: int = 8
COLUMN_COUNT: int = 8
PASTE_OFFSET: Pos = Pos(-21, -3, 0)


def make_data_schematic(datalist: list[int]) -> mcs.MCSchematic:
    schem = mcs.MCSchematic()
    pos_list: list[Pos] = []
    for row in range(ROW_COUNT): # rows
        for column in range(COLUMN_COUNT):
            even_pos = PASTE_OFFSET.copy().with_offset(column * 6, 0, 8 * row)
            odd_pos = even_pos.with_offset(0, 0, 4)
            pos_list.append(even_pos)
            pos_list.append(odd_pos)
    rawblocks: list[list[int]] = [datalist[i:i+4] for i in range(0, len(datalist), 4)]
    addr = 0
    for block_pos, block in zip(pos_list, rawblocks):
        while len(block) < 4:
            block.append(0)
        bytes = [bin(byte)[2:].rjust(8, '0') for byte in block]
        print(f"Datablock[{addr}]")
        for i, bit in enumerate(reversed(range(8))):
            bits = [byte[bit] for byte in bytes]
            power = 15
            for j, bit in enumerate(bits):
                if bit == '1':
                    power -= 2 ** j
            if power < 0:
                exit(f"invalid block bit: power={power}, values={block}")
            print(f"    power: {power}")
            bit_pos = block_pos.copy().with_offset(0, -2 * i, 0)
            schem.setBlock(bit_pos.tuple(), f"redstone_wire[power={power}]")
        addr += 1
    for block_pos in pos_list[len(rawblocks):]: # reset rest to zero
        for i, bit in enumerate(reversed(range(8))):
            bit_pos = block_pos.copy().with_offset(0, -2 * i, 0)
            schem.setBlock(bit_pos.tuple(), f"redstone_wire[power=0]")
    return schem

