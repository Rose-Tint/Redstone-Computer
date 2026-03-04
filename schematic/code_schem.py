import mcschematic as mcs
from .position import *


# Instruction Memory Diagram:
###                       ...
### 191, .. 133, 131, 129, | 193, 195, 197, .. 255
### 190, .. 132, 130, 128, | 192, 194, 196, .. 254
###
###  63, ..   5,   3,   1, |  65,  67,  69, .. 127
###  62, ..   4,   2,   0, *  64,  66,  68, .. 126
###
### paste spot = *
### Z-axis = south-north = up-down on the diagram; south > north
### X-axis = east-west = left-right on the diagram; east > west

MAX_INSTRUCTIONS: int = 1024 # 64 per half row * 2 halfs * 8 rows
ODD_OFFSET: Pos = Pos(0, 0, 4)
PASTE_OFFSET: Pos = Pos(-5, -2, -2) # SUBJECT TO CHANGE IF ROTATED
ZERO_BLOCK: str = "minecraft:obsidian"
ROW_COUNT: int = 8
SIDE_COLUMN_COUNT: int = 64


# if you need to rotate, change these
FORWARD = "south"
BACKWARD = "north"


def make_code_schematic(lines: list[str]) -> mcs.MCSchematic:
    MAX_INSTRUCTIONS = ROW_COUNT * SIDE_COLUMN_COUNT * 2
    schematic = mcs.MCSchematic()
    # the offset of the first instruction from where you will be pasting it
    pos_list: list[Pos] = []
    for row in range(ROW_COUNT): # rows
        ### left side:
        # position of the top block of the even instruction, offset by distance between rows
        left = PASTE_OFFSET.copy().with_offset(0, 0, 9 * row)
        left.x *= -1
        if row & 1:
            left.x -= 1
        # would be 64 but were doing the even and the odd in one iteration
        for i in range(SIDE_COLUMN_COUNT // 2):
            even: Pos = left.with_offset(2 * i, 0, 0)
            pos_list.append(even)
            pos_list.append(even.with_offset(ODD_OFFSET)) # odd
        ### right side:
        right = PASTE_OFFSET.copy().with_offset(0, 0, 9 * row)
        if row & 1:
            right.x += 1
        for i in range(SIDE_COLUMN_COUNT // 2):
            even = right.with_offset(-2 * i, 0, 0)
            pos_list.append(even)
            pos_list.append(even.with_offset(ODD_OFFSET)) # odd
    # Write instruction to each position
    # lines = [line.strip() for line in mc_file]
    while len(lines) < MAX_INSTRUCTIONS:
        lines.append("0000000000000000")
    for address, line in enumerate(lines):
        if len(line) != 16:
            exit("Invalid machine code file")
        direction = FORWARD if address & 1 else BACKWARD
        pos = pos_list[address].copy()
        byte1, byte2 = line[8:], line[:8]
        for ch in byte1:
            if ch == '1':
                schematic.setBlock(pos.tuple(), f"minecraft:repeater[facing={direction}]")
            else:
                schematic.setBlock(pos.tuple(), ZERO_BLOCK)
            pos.y -= 2
        pos.y -= 2
        for ch in byte2:
            if ch == '1':
                schematic.setBlock(pos.tuple(), f"minecraft:repeater[facing={direction}]")
            else:
                schematic.setBlock(pos.tuple(), ZERO_BLOCK)
            pos.y -= 2

    return schematic
