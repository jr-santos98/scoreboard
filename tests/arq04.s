.int 1 1
.mult 2 6
.add 2 2
.div 1 20
fld    F2,   0(x1)
fld    F3,   0(x2)
fmul F4,   F2, F3
fmul F5,   F3, F4
fadd  F3,   F3, F2
fdiv  F6,   F2, F4
fadd  F6,   F2, F4
