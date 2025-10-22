#ifndef VDBE_H
#define VDBE_H

#include "forth.h"
#include <sqlite3.h>

// Enhanced VDBE opcode definitions for Forth compilation
typedef enum {
    VDBE_INTEGER = 1,
    VDBE_ADD = 2,
    VDBE_SUBTRACT = 3,
    VDBE_MULTIPLY = 4,
    VDBE_DIVIDE = 5,
    VDBE_PRINT = 6,
    VDBE_DUP = 7,
    VDBE_DROP = 8,
    VDBE_SWAP = 9,
    VDBE_OVER = 10,
    VDBE_EMIT = 11,
    VDBE_CALL_WORD = 12,
    VDBE_RETURN = 13
} vdbe_opcode_t;

// VDBE instruction structure
typedef struct {
    vdbe_opcode_t opcode;
    int p1;  // First operand
    int p2;  // Second operand
    int p3;  // Third operand
} vdbe_instruction_t;

// VDBE program structure
typedef struct {
    vdbe_instruction_t *instructions;
    int instruction_count;
    int instruction_capacity;
} vdbe_program_t;

// VDBE compiler functions
int vdbe_init_program(vdbe_program_t *program);
void vdbe_cleanup_program(vdbe_program_t *program);
int vdbe_add_instruction(vdbe_program_t *program, vdbe_opcode_t opcode, int p1, int p2, int p3);
int vdbe_compile_to_sqlite(vdbe_program_t *program, sqlite3 *db, sqlite3_stmt **stmt);
int vdbe_execute_program(sqlite3_stmt *stmt, forth_vm_t *vm);

// Enhanced opcode emitters for Forth words
int vdbe_emit_stack_operation(vdbe_program_t *program, const char *operation);
int vdbe_emit_arithmetic(vdbe_program_t *program, const char *operation);
int vdbe_emit_io(vdbe_program_t *program, const char *operation);
int vdbe_emit_literal(vdbe_program_t *program, int value);

// VDBE to SQL translation
const char* vdbe_opcode_to_sql(vdbe_opcode_t opcode, int p1, int p2, int p3);
int vdbe_program_to_sql(vdbe_program_t *program, char *sql_buffer, size_t buffer_size);

#endif