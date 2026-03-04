.text
    @TEXT_DISPLAY_BUFFER = 15
    @TEXT_DISPLAY_FUNCTION = 14

.data
    string: cstring = "Hello, World!"

.code
    li $r1 string
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

