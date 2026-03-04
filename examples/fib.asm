.text
    @PORT_GPU = 1
    @PORT_GPU_X1 = 2
    @PORT_GPU_Y1 = 3
    @PORT_GPU_X2 = 4
    @PORT_GPU_Y2 = 5
    @SCREEN_BOTTOM = 1
    @SCREEN_TOP = 64
    @SCREEN_RIGHT = 1
    @SCREEN_LEFT = 64
    @SCREEN_HEIGHT = 63
    @SCREEN_WIDTH = 63
    @MAX_FIB = 255

.macro draw_pixel %x1 %y1
    wp %x1 @PORT_GPU_X1
    wp %y1 @PORT_GPU_Y1
    wp $zero @PORT_GPU
.endmacro

; sets %r1 to %r2
.macro move %r1 %r2
    add %r1 %r2 $zero
.endmacro

.code ; start
	li $r1 1 ; fib(n)
    li $r2 1 ; fib(n-1)
	li $r3 1 ; fib(n-2)
    main_loop_start:
        cmpi $r1 @MAX_FIB
        bgt main_loop_end ; while n < 255
        add $r1 $r2 $r3 ; n = fib(n-1) + fib(n-2)
        call draw_point
        move $r3 $r2 ; n2 = n1
        move $r2 $r1 ; n1 = n
    main_loop_end:
    exit

; $r1: number to plot
draw_point:
    push $r1
    push $r2
    li $r2 @SCREEN_TOP ; row = @SCREEN_TOP
    draw_point_loop_start:
        cmpi $r1 @SCREEN_LEFT
        blt draw_point_loop_end ; while n > @SCREEN_WIDTH:
        subi $r2 $r2 1 ; row -= 1
        subi $r1 $r1 @SCREEN_LEFT ; n -= @SCREEN_WIDTH
    draw_point_loop_end:
    draw_pixel $r1 $r2
    pop $r2
    pop $r1
    return

; ; $r1: number to print
; print_int:
;     push $r1
