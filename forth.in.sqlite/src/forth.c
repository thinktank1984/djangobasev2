#include "forth.h"

// Global VM pointer for primitive functions
static forth_vm_t *g_vm = NULL;

// VM initialization
int forth_init(forth_vm_t *vm, const char *db_path) {
    memset(vm, 0, sizeof(forth_vm_t));
    g_vm = vm;

    // Open SQLite database
    if (sqlite3_open(db_path, &vm->db) != SQLITE_OK) {
        forth_error("Failed to open database");
        return -1;
    }

    // Create tables for storing compiled words
    const char *create_words_table =
        "CREATE TABLE IF NOT EXISTS forth_words ("
        "name TEXT PRIMARY KEY,"
        "bytecode BLOB);";

    if (sqlite3_exec(vm->db, create_words_table, NULL, NULL, NULL) != SQLITE_OK) {
        forth_error("Failed to create words table");
        return -1;
    }

    // Initialize stack
    vm->stack_ptr = 0;

    // Add primitive words
    add_word(vm, "+", WORD_PRIMITIVE, prim_add);
    add_word(vm, "-", WORD_PRIMITIVE, prim_subtract);
    add_word(vm, "*", WORD_PRIMITIVE, prim_multiply);
    add_word(vm, "/", WORD_PRIMITIVE, prim_divide);
    add_word(vm, "dup", WORD_PRIMITIVE, prim_dup);
    add_word(vm, "drop", WORD_PRIMITIVE, prim_drop);
    add_word(vm, "swap", WORD_PRIMITIVE, prim_swap);
    add_word(vm, "over", WORD_PRIMITIVE, prim_over);
    add_word(vm, ".", WORD_PRIMITIVE, prim_dot);
    add_word(vm, "emit", WORD_PRIMITIVE, prim_emit);
    add_word(vm, ".s", WORD_PRIMITIVE, prim_stack_show);

    return 0;
}

void forth_cleanup(forth_vm_t *vm) {
    if (vm->db) {
        sqlite3_close(vm->db);
    }
    memset(vm, 0, sizeof(forth_vm_t));
}

// Stack operations
void push(forth_vm_t *vm, int value) {
    if (vm->stack_ptr >= STACK_SIZE) {
        forth_error("Stack overflow");
        return;
    }
    vm->data_stack[vm->stack_ptr++] = value;
}

int pop(forth_vm_t *vm) {
    if (vm->stack_ptr <= 0) {
        forth_error("Stack underflow");
        return 0;
    }
    return vm->data_stack[--vm->stack_ptr];
}

int stack_depth(forth_vm_t *vm) {
    return vm->stack_ptr;
}

// Dictionary operations
int find_word(forth_vm_t *vm, const char *name) {
    for (int i = vm->dict_size - 1; i >= 0; i--) {
        if (strcmp(vm->dictionary[i].name, name) == 0) {
            return i;
        }
    }
    return -1;
}

int add_word(forth_vm_t *vm, const char *name, word_type_t type, void *data) {
    if (vm->dict_size >= MAX_DICT_SIZE) {
        forth_error("Dictionary full");
        return -1;
    }

    strncpy(vm->dictionary[vm->dict_size].name, name, MAX_WORD_LEN - 1);
    vm->dictionary[vm->dict_size].name[MAX_WORD_LEN - 1] = '\0';
    vm->dictionary[vm->dict_size].type = type;

    if (type == WORD_PRIMITIVE) {
        vm->dictionary[vm->dict_size].data.prim_func = data;
    } else {
        vm->dictionary[vm->dict_size].data.compiled = (sqlite3_stmt*)data;
    }

    return vm->dict_size++;
}

// Primitive word implementations
void prim_add(void) {
    if (stack_depth(g_vm) < 2) {
        forth_error("Stack underflow in +");
        return;
    }
    int b = pop(g_vm);
    int a = pop(g_vm);
    push(g_vm, a + b);
}

void prim_subtract(void) {
    if (stack_depth(g_vm) < 2) {
        forth_error("Stack underflow in -");
        return;
    }
    int b = pop(g_vm);
    int a = pop(g_vm);
    push(g_vm, a - b);
}

void prim_multiply(void) {
    if (stack_depth(g_vm) < 2) {
        forth_error("Stack underflow in *");
        return;
    }
    int b = pop(g_vm);
    int a = pop(g_vm);
    push(g_vm, a * b);
}

void prim_divide(void) {
    if (stack_depth(g_vm) < 2) {
        forth_error("Stack underflow in /");
        return;
    }
    int b = pop(g_vm);
    if (b == 0) {
        forth_error("Division by zero");
        return;
    }
    int a = pop(g_vm);
    push(g_vm, a / b);
}

void prim_dup(void) {
    if (stack_depth(g_vm) < 1) {
        forth_error("Stack underflow in dup");
        return;
    }
    int value = pop(g_vm);
    push(g_vm, value);
    push(g_vm, value);
}

void prim_drop(void) {
    if (stack_depth(g_vm) < 1) {
        forth_error("Stack underflow in drop");
        return;
    }
    pop(g_vm);
}

void prim_swap(void) {
    if (stack_depth(g_vm) < 2) {
        forth_error("Stack underflow in swap");
        return;
    }
    int b = pop(g_vm);
    int a = pop(g_vm);
    push(g_vm, b);
    push(g_vm, a);
}

void prim_over(void) {
    if (stack_depth(g_vm) < 2) {
        forth_error("Stack underflow in over");
        return;
    }
    int b = pop(g_vm);
    int a = pop(g_vm);
    push(g_vm, a);
    push(g_vm, b);
    push(g_vm, a);
}

void prim_dot(void) {
    if (stack_depth(g_vm) < 1) {
        forth_error("Stack underflow in .");
        return;
    }
    int value = pop(g_vm);
    printf("%d ", value);
}

void prim_emit(void) {
    if (stack_depth(g_vm) < 1) {
        forth_error("Stack underflow in emit");
        return;
    }
    int value = pop(g_vm);
    putchar(value);
}

void prim_stack_show(void) {
    printf("<%d> ", stack_depth(g_vm));
    for (int i = g_vm->stack_ptr - 1; i >= 0; i--) {
        printf("%d ", g_vm->data_stack[i]);
    }
}

// SQLite VDBE operations
int vdbe_emit_integer(forth_vm_t *vm, int value) {
    if (!vm->current_stmt) {
        // Create a simple statement that returns the integer
        const char *sql = "SELECT ?";
        if (sqlite3_prepare_v2(vm->db, sql, -1, &vm->current_stmt, NULL) != SQLITE_OK) {
            forth_error("Failed to prepare integer statement");
            return -1;
        }
        sqlite3_bind_int(vm->current_stmt, 1, value);
    }
    return 0;
}

int vdbe_emit_add(forth_vm_t *vm) {
    if (!vm->current_stmt) {
        const char *sql = "SELECT ? + ?";
        if (sqlite3_prepare_v2(vm->db, sql, -1, &vm->current_stmt, NULL) != SQLITE_OK) {
            forth_error("Failed to prepare add statement");
            return -1;
        }
    }
    return 0;
}

int vdbe_emit_print(forth_vm_t *vm) {
    if (!vm->current_stmt) {
        const char *sql = "SELECT printf('%d', ?)";
        if (sqlite3_prepare_v2(vm->db, sql, -1, &vm->current_stmt, NULL) != SQLITE_OK) {
            forth_error("Failed to prepare print statement");
            return -1;
        }
    }
    return 0;
}

int vdbe_finalize_statement(forth_vm_t *vm, sqlite3_stmt **stmt) {
    (void)vm; // Suppress unused parameter warning
    if (*stmt) {
        sqlite3_finalize(*stmt);
        *stmt = NULL;
    }
    return 0;
}

// Parser and execution
int parse_token(forth_vm_t *vm, const char *token) {
    // Check if it's a number
    char *endptr;
    int value = strtol(token, &endptr, 10);
    if (*endptr == '\0') {
        // It's a number literal
        push(vm, value);
        return 0;
    }

    // Check if it's a word in the dictionary
    int word_idx = find_word(vm, token);
    if (word_idx >= 0) {
        forth_word_t *word = &vm->dictionary[word_idx];

        if (word->type == WORD_PRIMITIVE) {
            word->data.prim_func();
        } else if (word->type == WORD_COMPILED) {
            // Execute compiled SQLite statement
            sqlite3_stmt *stmt = word->data.compiled;
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                const char *result = (const char*)sqlite3_column_text(stmt, 0);
                if (result) {
                    printf("%s ", result);
                }
            }
            sqlite3_reset(stmt);
        }
        return 0;
    }

    fprintf(stderr, "Unknown word: %s\n", token);
    return -1;
}

int forth_execute(forth_vm_t *vm, const char *input) {
    char input_copy[MAX_INPUT_LEN];
    strncpy(input_copy, input, MAX_INPUT_LEN - 1);
    input_copy[MAX_INPUT_LEN - 1] = '\0';

    char *token = strtok(input_copy, " \t\n\r");
    while (token) {
        if (parse_token(vm, token) != 0) {
            return -1;
        }
        token = strtok(NULL, " \t\n\r");
    }

    return 0;
}

int forth_compile_word(forth_vm_t *vm, const char *name) {
    // This is a simplified compilation - in a full implementation,
    // we would build up VDBE opcodes and store them

    const char *sql = "SELECT 'Compiled word: ' || ?";
    sqlite3_stmt *stmt;
    if (sqlite3_prepare_v2(vm->db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        forth_error("Failed to prepare compiled word");
        return -1;
    }

    add_word(vm, name, WORD_COMPILED, stmt);

    // Store in database for persistence
    sqlite3_stmt *insert_stmt;
    const char *insert_sql = "INSERT OR REPLACE INTO forth_words (name, bytecode) VALUES (?, ?)";
    if (sqlite3_prepare_v2(vm->db, insert_sql, -1, &insert_stmt, NULL) == SQLITE_OK) {
        sqlite3_bind_text(insert_stmt, 1, name, -1, SQLITE_STATIC);
        // In a real implementation, we'd serialize the VDBE bytecode
        sqlite3_bind_blob(insert_stmt, 2, sql, strlen(sql), SQLITE_STATIC);
        sqlite3_step(insert_stmt);
        sqlite3_finalize(insert_stmt);
    }

    return 0;
}

void forth_error(const char *msg) {
    fprintf(stderr, "Forth Error: %s\n", msg);
}