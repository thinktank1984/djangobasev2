\ Interactive demonstration of Forth-in-SQLite

\ Show current stack (should be empty)
.s

\ Basic arithmetic
10 20 + .
\ Expected: 30

\ Stack manipulation
1 2 3 4 .s
dup . . . .
\ Expected stack: <4> 1 2 3 4
\ Expected output: 4 4 3 2 1

\ Define a new word that will be persisted
: double ( n -- 2*n ) dup + ;

\ Test the new word
15 double .
\ Expected: 30

\ Define a more complex word
: factorial ( n -- n! )
  dup 1 > if
    dup 1 - factorial *
  else
    drop 1
  then ;

\ Test factorial (this is simplified and will only work for small numbers)
5 factorial .
\ Expected: 120

\ Show all words including our new ones
words

\ Test persistence by creating a word
: hello-world 72 emit 101 emit 108 emit 108 emit 111 emit 32 emit 87 emit 111 emit 114 emit 108 emit 100 emit ;

hello-world
\ Expected: Hello World

\ Final stack check
.s