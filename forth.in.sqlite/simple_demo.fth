\ Simple interactive demonstration

\ Show empty stack
.s

\ Basic arithmetic
10 20 + .
\ Expected: 30

\ Stack operations
1 2 3 .s
dup . . .
\ Expected stack: <3> 1 2 3
\ Expected output: 3 3 2 1

\ Define a new word (this will be persisted)
: double dup + ;

\ Test the new word
15 double .
\ Expected: 30

\ Another word definition
: greet 72 emit 101 emit 108 emit 108 emit 111 emit ;

greet
\ Expected: Hello

\ Final stack state
.s