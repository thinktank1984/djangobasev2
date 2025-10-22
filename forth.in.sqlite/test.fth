\ Forth-in-SQLite Test Suite
\ Basic arithmetic tests

\ Test 1: Simple arithmetic
10 20 + .
\ Expected output: 30

\ Test 2: Stack operations
5 dup * .
\ Expected output: 25

\ Test 3: Multiple operations
3 4 5 + * .
\ Expected output: 27  (3 * (4 + 5))

\ Test 4: Complex stack manipulation
1 2 3 over over .
\ Expected output: 1 2 3 1 2

\ Test 5: Character output
65 emit 66 emit 67 emit
\ Expected output: ABC

\ Define a new word
: square ( n -- n^2 )
  dup * ;

\ Test the new word
7 square .
\ Expected output: 49

\ Define a more complex word
: cube ( n -- n^3 )
  dup square * ;

\ Test the cube word
3 cube .
\ Expected output: 27

\ Define a word that does output
: hello
  72 emit 101 emit 108 emit 108 emit 111 emit 32 emit ;

hello
\ Expected output: Hello

\ Test word composition
: fourth ( n -- n^4 )
  square square ;

2 fourth .
\ Expected output: 16

\ End of tests