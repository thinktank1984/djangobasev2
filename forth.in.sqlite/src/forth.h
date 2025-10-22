#ifndef FORTH_H
#define FORTH_H

#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// Maximum sizes
#define MAX_WORD_LEN 64
#define MAX_INPUT_LEN 1024
#define MAX_DICT_SIZE 1024
#define STACK_SIZE 256

// Word types
typedef enum {
    WORD_PRIMITIVE,
    WORD_COMPILED,
    WORD_IMMEDIATE
} word_type_t;

// Forth word definition
typedef struct {
    char name[MAX_WORD_LEN];
    word_type_t type;
    union {
        void (*prim_func)(void);  // For primitive words
        sqlite3_stmt *compiled;   // For compiled words
    } data;
} forth_word_t;

// Forth VM state
typedef struct {
    // Data stack
    int data_stack[STACK_SIZE];
    int stack_ptr;

    // Dictionary
    forth_word_t dictionary[MAX_DICT_SIZE];
    int dict_size;

    // SQLite database
    sqlite3 *db;

    // Compilation state
    int compiling;
    sqlite3_stmt *current_stmt;
} forth_vm_t;

// VM operations
int forth_init(forth_vm_t *vm, const char *db_path);
void forth_cleanup(forth_vm_t *vm);
int forth_execute(forth_vm_t *vm, const char *input);
int forth_compile_word(forth_vm_t *vm, const char *name);

// Stack operations
void push(forth_vm_t *vm, int value);
int pop(forth_vm_t *vm);
int stack_depth(forth_vm_t *vm);

// Primitive word functions
void prim_add(void);
void prim_subtract(void);
void prim_multiply(void);
void prim_divide(void);
void prim_dup(void);
void prim_drop(void);
void prim_swap(void);
void prim_over(void);
void prim_dot(void);
void prim_emit(void);
void prim_stack_show(void);

// SQLite VDBE operations
int vdbe_emit_integer(forth_vm_t *vm, int value);
int vdbe_emit_add(forth_vm_t *vm);
int vdbe_emit_print(forth_vm_t *vm);
int vdbe_finalize_statement(forth_vm_t *vm, sqlite3_stmt **stmt);

// Dictionary operations
int find_word(forth_vm_t *vm, const char *name);
int add_word(forth_vm_t *vm, const char *name, word_type_t type, void *data);

// Error handling
void forth_error(const char *msg);

#endif