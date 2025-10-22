\ Live demonstration of Forth-in-SQLite working

\ Show empty stack
.s

\ Basic arithmetic operations
5 7 + .
\ Expected: 12

\ Stack manipulation demonstration
3 dup * .
\ Expected: 9 (3 * 3)

\ More complex stack operations
1 2 3 over over . . . .
\ Expected: 3 2 1 3 2

\ Character output demo
72 emit 101 emit 108 emit 108 emit 111 emit 32 emit
\ Expected: Hello

\ Final stack check
.s