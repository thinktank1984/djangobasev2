#include "compiler.h"

// Initialize compiler
int compiler_init(forth_compiler_t *compiler, forth_vm_t *vm) {
    if (!compiler || !vm) return -1;

    compiler->vm = vm;
    compiler->state = COMPILER_INTERPRETING;
    compiler->current_word[0] = '\0';

    return vdbe_init_program(&compiler->current_program);
}

void compiler_cleanup(forth_compiler_t *compiler) {
    if (compiler) {
        vdbe_cleanup_program(&compiler->current_program);
        memset(compiler, 0, sizeof(forth_compiler_t));
    }
}

// Start compiling a new word
int compiler_start_word(forth_compiler_t *compiler, const char *word_name) {
    if (!compiler || !word_name) return -1;

    strncpy(compiler->current_word, word_name, MAX_WORD_LEN - 1);
    compiler->current_word[MAX_WORD_LEN - 1] = '\0';
    compiler->state = COMPILER_COMPILING;

    // Clear current program
    vdbe_cleanup_program(&compiler->current_program);
    vdbe_init_program(&compiler->current_program);

    printf("Compiling word: %s\n", word_name);
    return 0;
}

// End word compilation
int compiler_end_word(forth_compiler_t *compiler) {
    if (!compiler || compiler->state != COMPILER_COMPILING) return -1;

    // Compile the VDBE program to SQLite
    sqlite3_stmt *stmt;
    if (vdbe_compile_to_sqlite(&compiler->current_program, compiler->vm->db, &stmt) != 0) {
        compiler_error(compiler, "Failed to compile word to SQLite");
        return -1;
    }

    // Add word to dictionary
    add_word(compiler->vm, compiler->current_word, WORD_COMPILED, stmt);

    // Save to database for persistence
    compiler_save_word(compiler, compiler->current_word, &compiler->current_program);

    printf("Compiled word: %s\n", compiler->current_word);

    // Reset compiler state
    compiler->state = COMPILER_INTERPRETING;
    compiler->current_word[0] = '\0';

    return 0;
}

// Compile a token during word definition
int compiler_compile_token(forth_compiler_t *compiler, const char *token) {
    if (!compiler || !token) return -1;

    // Check if it's a literal number
    char *endptr;
    int value = strtol(token, &endptr, 10);
    if (*endptr == '\0') {
        return compiler_compile_literal(compiler, value);
    }

    // Handle special compiling words
    if (strcmp(token, ";") == 0) {
        return compiler_end_word(compiler);
    }

    // Check if it's an immediate word (handled during compilation)
    int word_idx = find_word(compiler->vm, token);
    if (word_idx >= 0) {
        forth_word_t *word = &compiler->vm->dictionary[word_idx];
        if (word->type == WORD_IMMEDIATE) {
            word->data.prim_func();
            return 0;
        }
    }

    // Compile word call
    return compiler_compile_word_call(compiler, token);
}

// Compile a literal
int compiler_compile_literal(forth_compiler_t *compiler, int value) {
    return vdbe_emit_literal(&compiler->current_program, value);
}

// Compile a primitive word
int compiler_compile_primitive(forth_compiler_t *compiler, const char *word_name) {
    // Emit appropriate VDBE instruction for primitive
    if (strcmp(word_name, "+") == 0 || strcmp(word_name, "-") == 0 ||
        strcmp(word_name, "*") == 0 || strcmp(word_name, "/") == 0) {
        return vdbe_emit_arithmetic(&compiler->current_program, word_name);
    } else if (strcmp(word_name, ".") == 0 || strcmp(word_name, "emit") == 0) {
        return vdbe_emit_io(&compiler->current_program, word_name);
    } else if (strcmp(word_name, "dup") == 0 || strcmp(word_name, "drop") == 0 ||
               strcmp(word_name, "swap") == 0 || strcmp(word_name, "over") == 0) {
        return vdbe_emit_stack_operation(&compiler->current_program, word_name);
    }

    return -1;
}

// Compile a word call
int compiler_compile_word_call(forth_compiler_t *compiler, const char *word_name) {
    // Check if it's a primitive
    int word_idx = find_word(compiler->vm, word_name);
    if (word_idx >= 0) {
        forth_word_t *word = &compiler->vm->dictionary[word_idx];
        if (word->type == WORD_PRIMITIVE) {
            return compiler_compile_primitive(compiler, word_name);
        }
    }

    // For now, we'll create a simple SQL call
    char sql[256];
    snprintf(sql, sizeof(sql), "SELECT '%s word executed'", word_name);
    vdbe_add_instruction(&compiler->current_program, VDBE_PRINT, 0, 0, 0);

    return 0;
}

// Save compiled word to database
int compiler_save_word(forth_compiler_t *compiler, const char *name, vdbe_program_t *program) {
    if (!compiler || !name || !program) return -1;

    // Serialize the program
    size_t program_size = program->instruction_count * sizeof(vdbe_instruction_t);
    void *program_blob = malloc(program_size);
    if (!program_blob) return -1;

    memcpy(program_blob, program->instructions, program_size);

    // Save to database
    sqlite3_stmt *stmt;
    const char *sql = "INSERT OR REPLACE INTO forth_words (name, bytecode) VALUES (?, ?)";
    if (sqlite3_prepare_v2(compiler->vm->db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        free(program_blob);
        return -1;
    }

    sqlite3_bind_text(stmt, 1, name, -1, SQLITE_STATIC);
    sqlite3_bind_blob(stmt, 2, program_blob, program_size, SQLITE_STATIC);

    int result = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    free(program_blob);

    return (result == SQLITE_DONE) ? 0 : -1;
}

// Load compiled word from database
int compiler_load_word(forth_compiler_t *compiler, const char *name) {
    if (!compiler || !name) return -1;

    sqlite3_stmt *stmt;
    const char *sql = "SELECT bytecode FROM forth_words WHERE name = ?";
    if (sqlite3_prepare_v2(compiler->vm->db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return -1;
    }

    sqlite3_bind_text(stmt, 1, name, -1, SQLITE_STATIC);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const void *blob = sqlite3_column_blob(stmt, 0);
        int blob_size = sqlite3_column_bytes(stmt, 0);

        if (blob && blob_size > 0) {
            // Deserialize program
            vdbe_program_t program;
            vdbe_init_program(&program);

            int instruction_count = blob_size / sizeof(vdbe_instruction_t);
            vdbe_instruction_t *instructions = (vdbe_instruction_t*)blob;

            for (int i = 0; i < instruction_count; i++) {
                vdbe_add_instruction(&program, instructions[i].opcode,
                                    instructions[i].p1, instructions[i].p2, instructions[i].p3);
            }

            // Compile to SQLite statement
            sqlite3_stmt *compiled_stmt;
            if (vdbe_compile_to_sqlite(&program, compiler->vm->db, &compiled_stmt) == 0) {
                add_word(compiler->vm, name, WORD_COMPILED, compiled_stmt);
                printf("Loaded word: %s\n", name);
            }

            vdbe_cleanup_program(&program);
        }
    }

    sqlite3_finalize(stmt);
    return 0;
}

// Load all saved words from database
int compiler_load_all_words(forth_compiler_t *compiler) {
    if (!compiler) return -1;

    sqlite3_stmt *stmt;
    const char *sql = "SELECT name FROM forth_words";
    if (sqlite3_prepare_v2(compiler->vm->db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return -1;
    }

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *name = (const char*)sqlite3_column_text(stmt, 0);
        if (name) {
            compiler_load_word(compiler, name);
        }
    }

    sqlite3_finalize(stmt);
    return 0;
}

// Error handling
void compiler_error(forth_compiler_t *compiler, const char *msg) {
    fprintf(stderr, "Compiler Error: %s\n", msg);
    if (compiler && compiler->state == COMPILER_COMPILING) {
        compiler->state = COMPILER_INTERPRETING;
        compiler->current_word[0] = '\0';
    }
}