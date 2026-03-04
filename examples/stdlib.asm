.text
@PORT_SCREEN_OPCODE = 1
@PORT_SCREEN_L1X = 2
@PORT_SCREEN_L1Y = 3
@PORT_SCREEN_L2X = 4
@PORT_SCREEN_L2Y = 5
@PORT_KEYBOARD_INPUT = 6
@PORT_KEYBOARD_READY = 7
@PORT_TEXT_DISPLAY_BUFFER = 8
@PORT_TEXT_DISPLAY_SET = 9
@KEYBOARD_MAX_SIZE = 32

@NEXT_FREE_ADDR = 0

; uses $r7
; if value of %output is 0, allocation failed
.macro @alloc %size %output
    lw %output [@NEXT_FREE_ADDR]
    li $r7 %size
    addi $r7 $r7 1
    sw %r7 [%output]
    addi $r7 %output %size
    sw $r7 [@NEXT_FREE_ADDR]
.endmacro

.macro @strlen %addr %output
    lw %output [%addr]
    subi %output %output 1
.endmacro

.macro @index %addr %i %output
    addi %addr %addr %i
    addi %addr %addr 1
    lw %output [%addr]
.endmacro

.macro @inc %r
    addi %r %r 1
.endmacro

.macro @sub %r
    subi %r %r 1
.endmacro

; uses $r7, $r6, $r5
.macro @print %str
    lw $r7 [%str]
    add $r7 %str $r7    ; r7 = final char addr
    addi $r6 %str 1     ; r6 = char addr
    start:
        lw $r5 [$r6]
        wp $r5 @PORT_TEXT_DISPLAY_BUFFER
        addi $r6 %r6 1
        cmp $r6 $r7
        ble start
        wp $zero @PORT_TEXT_DISPLAY_SET ; push buffer
.endmacro

; PARAMS:
; $r1 - pointer to 32 bytes
readline:
    li $r7 @KEYBOARD_MAX_SIZE ; input counter
    readline_loop_start:
        ; break if keyboard is not ready (no more input)
        rp $r5 @PORT_KEYBOARD_READY
        cmp $r5 $zero
        beq readline_loop_end
        ; or we have hit the end of the queue
        cmp $r7 $zero
        beq readline_loop_end
        subi $r7 $r7 1 ; decrement
        ; or we have hit the end of the queue
        cmp $r6 $zero
        beq readline_loop_end
        addi $r6 $r6 1 ; increment
        rp $r5 @PORT_KEYBOARD_INPUT
        cmp $r5 $r4 ; handle backspaces
        beq readline_backspace
        readline_backspace:
            subi $r6 $r6 1



    readline_loop_end:
    return


