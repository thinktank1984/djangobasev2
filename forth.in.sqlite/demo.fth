\ Forth-in-SQLite Demonstration
\ Shows the concept of Forth compiling to SQLite VDBE

\ Basic arithmetic demonstration
\ These use the primitive words implemented in C
10 20 + .
\ This pushes 10, pushes 20, then calls the + primitive
\ Expected: 30

\ Stack manipulation demo
1 2 3 dup . . . .
\ Expected: 3 3 2 1

\ Define a new word that gets compiled to SQLite
: add-and-print ( a b -- )
  + . ;

\ Test the compiled word
15 25 add-and-print
\ Expected: 40

\ Define a word that demonstrates persistence
: counter 0 ;
\ This creates a word that will be stored in the SQLite database

\ More complex compilation example
: math-demo
  5 6 7 + * . ;

math-demo
\ Expected: 65 (5 * (6 + 7))

\ Show that words persist (check database afterwards)
: persistent-word ( -- )
  100 200 + . ;

persistent-word
\ Expected: 300

\ The words 'add-and-print', 'math-demo', and 'persistent-word'
\ are now stored as SQLite bytecode in the forth.db file
\ and can be reloaded in future sessions!

\ Final demonstration of compilation vs interpretation
\ This shows how Forth words become SQLite statements
: compilation-demo
  \ This compiles to: SELECT printf('%d ', (10 + 20) * 2)
  10 20 + 2 * . ;

compilation-demo
\ Expected: 60