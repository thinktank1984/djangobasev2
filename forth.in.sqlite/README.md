# Forth-in-SQLite: A Persistent Forth Runtime Powered by SQLite

This project implements a Forth programming language system that compiles to SQLite's VDBE (Virtual Database Engine) bytecode, creating a persistent, transactional Forth environment.

## Concept

Forth-in-SQLite treats SQLite's VDBE as a target for Forth compilation. Instead of compiling to native Forth opcodes, words are compiled to SQLite opcodes and executed through SQLite's engine. This creates:

- **Persistent Environment**: Forth words and data share the same SQLite database file
- **Transactional Safety**: All operations run within SQLite's transactional sandbox
- **Portability**: Works wherever SQLite works (embedded, mobile, etc.)
- **Extensibility**: Can create DSLs that compile to SQL operations

## Architecture

```
[Forth Source] → [Forth Parser] → [SQLite Opcode Generator] → [SQLite VDBE Execution]
```

Each Forth word definition becomes a stored procedure backed by SQLite's VDBE bytecode.

## Features

### Core Forth Primitives
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Stack Operations**: `dup`, `drop`, `swap`, `over`
- **I/O**: `.`, `emit`

### Word Definition
Define new words using standard Forth syntax:
```forth
: square ( n -- n^2 ) dup * ;
: add-and-print ( a b -- ) + . ;
```

### Persistence
Compiled words are automatically stored in the SQLite database and reloaded on startup:
```forth
: persistent-word ( -- ) 100 200 + . ;
```

## Building and Running

### Prerequisites
- GCC compiler
- SQLite development libraries
- Make

### Build
```bash
make clean
make
```

### Run Demo
```bash
make demo
# or
./bin/forth-sqlite demo.fth
```

### Run Tests
```bash
make test
# or
./bin/forth-sqlite test.fth
```

### Interactive Mode
```bash
./bin/forth-sqlite
```

## REPL Commands

- `: name ... ;` - Define a new word
- `.s` - Show stack contents
- `words` - List all defined words
- `help` - Show help
- `quit` - Exit the REPL

## Example Usage

### Basic Arithmetic
```forth
10 20 + .          \ Output: 30
5 dup * .          \ Output: 25
```

### Word Definition
```forth
: square dup * ;   \ Define square word
7 square .         \ Output: 49
```

### Persistence Example
```forth
: hello 72 emit 101 emit 108 emit 108 emit 111 emit ;
hello              \ Output: Hello
```

The `hello` word is now stored in the database and available in future sessions.

## Technical Implementation

### VDBE Compilation
Forth words are compiled to SQLite opcodes:
- `10 20 +` → `SELECT 10 + 20`
- `dup *` → `SELECT ? * ?` (with appropriate parameter binding)

### Database Schema
```sql
CREATE TABLE forth_words (
    name TEXT PRIMARY KEY,
    bytecode BLOB
);
```

### Component Structure
- **forth.h/c**: Core Forth VM and primitives
- **vdbe.h/c**: SQLite VDBE opcode generation and compilation
- **compiler.h/c**: Forth word compilation and persistence
- **main.c**: REPL interface and file execution

## Future Enhancements

- Enhanced VDBE opcode coverage
- More sophisticated compilation strategies
- SQL integration words
- Transaction control words
- Database schema manipulation words
- Performance optimization

## License

This project demonstrates the concept of treating SQLite as a Forth execution backend. It's designed for educational and experimental purposes to explore the intersection of programming language implementation and database systems.