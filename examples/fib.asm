.text
@SEQ_LEN = 10

.code
    li $r1 1 ; counter
	li $r2 1 ; fib(n-1)
	li $r3 0 ; fib(n-2)
	li $r4 0 ; fib(n)
loop_start:
        li $r7 @SEQ_LEN
        cmp $r1 $r7
		bgt loop_end
		add $r6 $r2 $r3
        add $r3 $r2 $zero ; move $r3 $r2
        add $r2 $r6 $zero ; move $r2 $r6
        li $r5 1
		add $r1 $r1 $r5
		jmp loop_start
loop_end:
    exit
