
.code
; params:
;   $r1: pointer to cstring to print
write_cstr:
    rp $zero @TEXT_DISPLAY_FUNCTION
    loop_start:
        lw $r2 [$r1]
        cmp $r2 $zero
        beq loop_end
        wp $r1 @TEXT_DISPLAY_BUFFER
        addi $r1 $r1 1
        jump loop_start
    loop_end:
    wp $zero @TEXT_DISPLAY_FUNCTION
