.text
    @PIPE_X_GAP = 8 ; horizontal gap between different pipes
    @PIPE_Y_GAP = 6 ; gap in the pipe
    @BOUNCE_HEIGHT = 3
    @PLAYER_X = 28
    @WINDOW_TOP = 33
    @PORT_TEXT_DISPLAY_BUFFER = 8
    @PORT_TEXT_DISPLAY_FUNCTION = 9
    @PORT_RNG = 10
    @PORT_MOUSE = 11

.data
    player_y: word 0
    score: word 0
    #align 4
    pipe1_x: word 0
    pipe2_x: word 0
    pipe3_x: word 0
    pipe4_x: word 0
    pipe1_y: word 0
    pipe2_y: word 0
    pipe3_y: word 0
    pipe4_y: word 0
    loading_str: string "LOADING..."
    ready_str: string "READY?"
    go_str: string "GO!"
    game_over_str: string "GAME OVER!"

.macro load %reg %addr
    li %reg %addr
    lw %reg [%reg]
.endmacro

.macro inc %r
    addi %r %r 1
.endmacro

.macro dec %r
    subi %r %r 1
.endmacro

.code ; start
    li $r1 loading_str
    call print
    call draw_frame
    li $r1 ready_str
    call print
    li $r1 go_str
    call print
    main_loop_start:
        call detect_bounce
        call shift_pipes_left
        ; check if need to cycle pipes
        ; cycle if pipe1_x < @PLAYER_X - 1
        load $r1 pipe1_x
        inc $r1
        cmpi $r1 @PLAYER_X
        blt main_loop_no_cycle
            call cycle_pipes
        main_loop_no_cycle:
        ; call detect_collision
        ; if collided:
        ; jump main_loop_end ; branch
        ; call detect_bounce
        call draw_frame
        li $r1 score
        lw $r2 [$r1]
        inc $r1
        sw $r2 [$r1]
        jump main_loop_start
    main_loop_end:
    li $r1 game_over_str
    call print
    exit

draw_frame:
    push $r1
    push $r2
    push $r3
    push $r4
    push $r6
    push $r7
    li $r7 pipe4_x
    li $r6 pipe4_y
    draw_frame_pipe_start:
        li $r7 pipe1_x
        lw $r1 [$r7]                ; ; x1,x2 = pipe_x
        li $r6 pipe1_y
        lw $r2 [$r6]                ; y1 = pipe_y
        li $r3 @SCREEN_BOTTOM       ; y2 = @SCREEN_BOTTOM
        draw_square $r1 $r2 $r1 $r3
        addi $r2 $r2 @PIPE_Y_GAP    ; y2 = pipe_y + @PIPE_Y_GAP
        li $r3 @WINDOW_TOP          ; y1 = @WINDOW_TOP
        draw_square $r1 $r2 $r1 $r3
        dec $r7
        dec $r6
        cmpi $r7 pipe1_x
        bge draw_frame_pipe_start
    ; player
    ;   draw sprite OR:
    li $r1 @PLAYER_X    ; x = PLAYER_X
    load $r2 player_y   ; y = player_y
    draw_pixel $r1 $r2
    addi $r3 $r2 1      ; y = player_y + 1
    draw_pixel $r1 $r3
    dec $r1             ; x = PLAYER_X - 1
    draw_pixel $r1 $r2
    pop $r1
    pop $r2
    pop $r3
    pop $r4
    pop $r6
    pop $r7
    return

cycle_pipes:
    push $r1
    push $r2
    push $r3
    push $r4
    ; pipe1_x += @PIPE_X_GAP
    li $r1 pipe1_x
    lw $r2 [$r1]
    addi $r2 $r2 @PIPE_X_GAP
    sw $r2 [$r1]
    ; pipe2_x += @PIPE_X_GAP
    li $r1 pipe2_x
    lw $r2 [$r1]
    addi $r2 $r2 @PIPE_X_GAP
    sw $r2 [$r1]
    ; pipe3_x += @PIPE_X_GAP
    li $r1 pipe3_x
    lw $r2 [$r1]
    addi $r2 $r2 @PIPE_X_GAP
    sw $r2 [$r1]
    ; pipe4_x += @PIPE_X_GAP
    li $r1 pipe4_x
    lw $r2 [$r1]
    addi $r2 $r2 @PIPE_X_GAP
    sw $r2 [$r1]
    li $r1 pipe2_y
    lw $r2 [$r1]
    li $r1 pipe3_y
    lw $r3 [$r1]
    li $r1 pipe4_y
    lw $r4 [$r1]
    li $r1 pipe2_y
    sw $r2 [$r1]
    li $r1 pipe3_y
    sw $r3 [$r1]
    li $r1 pipe4_y
    sw $r4 [$r1]
    rp $r2 @PORT_RNG
    shl $r2 $r2
    shl $r2 $r2
    shl $r2 $r2
    shl $r2 $r2
    li $r1 pipe4_y
    sw $r2 [$r1]
    pop $r4
    pop $r3
    pop $r2
    pop $r1
    return

shift_pipes_left:
    push $r1
    push $r2
    li $r1 pipe1_x ; r1 = pipe address
    shift_left_loop_start:
        lw $r2 [$r1] ; r2 = x position of pipe
        inc $r2 ; move pipe x left 1
        sw $r2 [$r1]
        inc $r1 ; go to next pipe
        cmpi $r1 pipe4_x
        ble shift_left_loop_start
    pop $r2
    pop $r1
    return

detect_bounce:
    push $r1
    push $r2
    push $r3
    rp $r1 @PORT_MOUSE
    li $r2 player_y
    detect_bounce_loop_start:
        cmpi $r1 0
        bne detect_bounce_loop_start
        lw $r3 [$r2]
        addi $r3 $r3 @BOUNCE_HEIGHT
        dec $r1
    detect_bounce_loop_end:
    pop $r3
    pop $r2
    pop $r1
    return
;     return
    ; if click:
    ;   player_y += @BOUNCE_HEIGHT

; return:
;   $r7: 1 on collision, 0 on no collision
; detect_collision:
;     return
    ; collision if:
    ;   @PLAYER_X == pipe1_x ; body
    ;       & (player_y <= pipe1_y)
    ;   @PLAYER_X == pipe1_x ; wing
    ;       & (player_y + 1 > pipe1_y + @PIPE_Y_GAP)
    ;   @PLAYER_X - 1 == pipe1_x ; tail
    ;       & (player_y <= pipe1_y | player_y > pipe1_y + @PIPE_Y_GAP)

; params:
;   $r1: pointer to string start
print:
    push $r1
    push $r2
    print_loop_start:
        lw $r2 [$r1]
        inc $r1
        cmp $r2 $zero
        beq print_loop_end
        wp $r2 @PORT_TEXT_DISPLAY_BUFFER
        jump print_loop_start
    print_loop_end:
    wp $zero @PORT_TEXT_DISPLAY_FUNCTION
    pop $r2
    pop $r1
    return


.import "graphics.asm"
