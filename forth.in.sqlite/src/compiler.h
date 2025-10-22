#ifndef COMPILER_H
#define COMPILER_H

#include "forth.h"
#include "vdbe.h"

// Compiler state
typedef enum {
    COMPILER_INTERPRETING,
    COMPILER_COMPILING
} compiler_state_t;

// Forth compiler
typedef struct {
    forth_vm_t *vm;
    compiler_state_t state;
    vdbe_program_t current_program;
    char current_word[MAX_WORD_LEN];
} forth_compiler_t;

// Compiler initialization
int compiler_init(forth_compiler_t *compiler, forth_vm_t *vm);
void compiler_cleanup(forth_compiler_t *compiler);

// Compilation control
int compiler_start_word(forth_compiler_t *compiler, const char *word_name);
int compiler_end_word(forth_compiler_t *compiler);
int compiler_compile_token(forth_compiler_t *compiler, const char *token);

// Word compilation
int compiler_compile_literal(forth_compiler_t *compiler, int value);
int compiler_compile_primitive(forth_compiler_t *compiler, const char *word_name);
int compiler_compile_word_call(forth_compiler_t *compiler, const char *word_name);

// Special compiling words
int compiler_handle_colon(forth_compiler_t *compiler, const char *word_name);
int compiler_handle_semicolon(forth_compiler_t *compiler);
int compiler_handle_immediate(forth_compiler_t *compiler, const char *word_name);

// Database persistence
int compiler_save_word(forth_compiler_t *compiler, const char *name, vdbe_program_t *program);
int compiler_load_word(forth_compiler_t *compiler, const char *name);
int compiler_load_all_words(forth_compiler_t *compiler);

// Error handling
void compiler_error(forth_compiler_t *compiler, const char *msg);

#endif