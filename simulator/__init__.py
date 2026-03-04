from asyncio import sleep
from threading import Thread
from assembler import Program
from gui import launch_gui, GUI
from gui.control import RunState
from .common import *
from .cpu import CPU
from .io_ports import *
from .inputs import *
from .inputs.pixel_display import *


async def run_simulator(program: Program) -> None:
    gui = GUI(program)
    cpu = CPU(gui)
    cpu.instructions.load(program.code)
    cpu.ram.load(program.data)
    keyboard = Keyboard(gui.keyboard, cpu.ports[6], cpu.ports[7])
    text_display = TextDisplay(gui.text_display, cpu.ports[8], cpu.ports[9])
    pixel_display = PixelDisplay(gui.pixel_display, cpu.ports[1], cpu.ports[2], cpu.ports[3], cpu.ports[4], cpu.ports[5])
    rng = RNG(cpu.ports[10])
    launch_gui(gui)
    # ui_thread = Thread(target=launch_gui, args=(gui,))
    # ui_thread.start()
    # while not cpu.finished:
    #     print("DEBUG: in cpu loop")
    #     match gui.program_control.run_state:
    #         case RunState.PAUSED:
    #             continue
    #         case RunState.RUNNING:
    #             await sleep(1 / gui.program_control.rate)
    #         case RunState.STEP:
    #             gui.program_control.set_state(RunState.PAUSED)
    #     instruction = cpu.instructions.advance()
    #     gui.code_display.highlight(cpu.instructions.pc - 1)
    #     cpu.execute(instruction)
    #     gui.registers.update_registers(cpu.regs.registers[1:])
    #     gui.ram.update_ram(cpu.ram.ram)
    # ui_thread.join()