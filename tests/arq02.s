.int 2 1
.mult 2 4
.add 1 2
.div 1 10
fld f1, 0(x1)
fld f5, 0(x1)
fdiv f2, f4, f5
fmul f4, f8, f9
fadd f1, f2, f3 
fsd f4, 0(x2)
