.text
    @PORT_GPU = 1
    @PORT_GPU_X1 = 2
    @PORT_GPU_Y1 = 3
    @PORT_GPU_X2 = 4
    @PORT_GPU_Y2 = 5
    @SCREEN_BOTTOM = 1
    @SCREEN_TOP = 64

.macro draw_pixel %x1 %y1
    wp %x1 @PORT_GPU_X1
    wp %y1 @PORT_GPU_Y1
    wp $zero @PORT_GPU_X2
    wp $zero @PORT_GPU_Y2
    wp $zero @PORT_GPU
.endmacro

.macro draw_square %x1 %y1 %x2 %y2
    wp %x1 @PORT_GPU_X1
    wp %y1 @PORT_GPU_Y1
    wp %x2 @PORT_GPU_X2
    wp %y2 @PORT_GPU_Y2
    wp $zero @PORT_GPU
.endmacro

.macro clear_screen
    wp $zero @PORT_GPU
.endmacro
