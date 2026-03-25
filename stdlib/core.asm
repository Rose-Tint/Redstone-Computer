.macro inc %r
    addi %r %r 1
.endmacro

.macro dec %r
    subi %r %r 1
.endmacro

.macro load %reg %addr
    li %reg %addr
    lw %reg [%reg]
.endmacro
