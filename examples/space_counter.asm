.text
@NUM_DISPLAY = 1
@KB_INPUT = 5
@KB_READY = 6

.code
    ; while port @KB_READY < 1
    ; if port @KB_INPUT == 32 (space in ascii)
    ;   increment $r2 and write it to port @NUM_DISPLAY
    li $r2 0
start:
    call wait_for_input
    li $r7 32
    cmp $r1 $r7
    bne startb 
    addi $r2 $r2 1
    wp $r2 @NUM_DISPLAY
    jmp start


wait_for_input:
    rp $r1 @KB_READY
    li $r7 1
    cmp $r1 $r7
    blt wait_for_input
    rp $r1 @KB_INPUT
    return
