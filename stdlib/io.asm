.import "core.asm"

.text
    @PORT_TEXT_DISPLAY_BUFFER = 8
    @PORT_TEXT_DISPLAY_FUNCTION = 9


.macro clear_text
    rp $zero @PORT_TEXT_DISPLAY_FUNCTION
.endmacro

.macro push_text
    wp $zero @PORT_TEXT_DISPLAY_FUNCTION
.endmacro

.macro println %s
    push $r1
    li $r1 %s
    call print_str_ln
    pop $r1
.endmacro


.code
; params:
;   $r1: pointer to null-terminated string to write
write_str:
    push $r1
    push $r2
    __write_str_loop_start:
        lw $r2 [$r1]
        cmp $r2 $zero
        beq __write_str_loop_end
        wp $r2 @PORT_TEXT_DISPLAY_BUFFER
        inc $r1
        jump __write_str_loop_start
    __write_str_loop_end:
    pop $r2
    pop $r1
    return

; params:
;   $r1: pointer to null-terminated string to print
print_str_ln:
    rp $zero @PORT_TEXT_DISPLAY_FUNCTION
    call write_str
    wp $zero @PORT_TEXT_DISPLAY_FUNCTION
