from typing import TypeAlias


Word: TypeAlias = int

Addr: TypeAlias = int

class InterpreterError(Exception): pass

def bounds_check(n: Word) -> Word:
    if -128 > n or n > 255:
        raise InterpreterError(f"word out of bounds ({n})")
    else:
        return n

def clamp(min: int, max: int, x: int) -> int:
    if x < min: x = min
    if x > max: x = max
    return x

def clamp_word(n: Word) -> Word:
    return clamp(-127, 255, n)
