#include "vdbe.h"

// Initialize a VDBE program
int vdbe_init_program(vdbe_program_t *program) {
    if (!program) return -1;

    program->instruction_capacity = 64;
    program->instruction_count = 0;
    program->instructions = malloc(program->instruction_capacity * sizeof(vdbe_instruction_t));

    if (!program->instructions) {
        return -1;
    }

    return 0;
}

void vdbe_cleanup_program(vdbe_program_t *program) {
    if (program && program->instructions) {
        free(program->instructions);
        program->instructions = NULL;
        program->instruction_count = 0;
        program->instruction_capacity = 0;
    }
}

int vdbe_add_instruction(vdbe_program_t *program, vdbe_opcode_t opcode, int p1, int p2, int p3) {
    if (!program || !program->instructions) return -1;

    // Resize if needed
    if (program->instruction_count >= program->instruction_capacity) {
        program->instruction_capacity *= 2;
        vdbe_instruction_t *new_instructions = realloc(program->instructions,
            program->instruction_capacity * sizeof(vdbe_instruction_t));
        if (!new_instructions) {
            return -1;
        }
        program->instructions = new_instructions;
    }

    // Add instruction
    vdbe_instruction_t *instr = &program->instructions[program->instruction_count++];
    instr->opcode = opcode;
    instr->p1 = p1;
    instr->p2 = p2;
    instr->p3 = p3;

    return 0;
}

// Convert VDBE opcode to SQL representation
const char* vdbe_opcode_to_sql(vdbe_opcode_t opcode, int p1, int p2, int p3) {
    (void)p2; (void)p3; // Suppress unused parameter warnings
    static char sql_buffer[256];

    switch (opcode) {
        case VDBE_INTEGER:
            snprintf(sql_buffer, sizeof(sql_buffer), "%d", p1);
            break;

        case VDBE_ADD:
            snprintf(sql_buffer, sizeof(sql_buffer), "(%s + %s)",
                "?1", "?2");
            break;

        case VDBE_SUBTRACT:
            snprintf(sql_buffer, sizeof(sql_buffer), "(%s - %s)",
                "?1", "?2");
            break;

        case VDBE_MULTIPLY:
            snprintf(sql_buffer, sizeof(sql_buffer), "(%s * %s)",
                "?1", "?2");
            break;

        case VDBE_DIVIDE:
            snprintf(sql_buffer, sizeof(sql_buffer), "(%s / %s)",
                "?1", "?2");
            break;

        case VDBE_PRINT:
            snprintf(sql_buffer, sizeof(sql_buffer), "printf('%%d ', %s)", "?1");
            break;

        case VDBE_EMIT:
            snprintf(sql_buffer, sizeof(sql_buffer), "char(%s)", "?1");
            break;

        case VDBE_DUP:
            snprintf(sql_buffer, sizeof(sql_buffer), "%s", "?1");
            break;

        default:
            snprintf(sql_buffer, sizeof(sql_buffer), "SELECT 'Unknown opcode: %d'", opcode);
            break;
    }

    return sql_buffer;
}

// Convert entire VDBE program to SQL
int vdbe_program_to_sql(vdbe_program_t *program, char *sql_buffer, size_t buffer_size) {
    if (!program || !sql_buffer || buffer_size == 0) return -1;

    // Start building the SQL
    snprintf(sql_buffer, buffer_size, "SELECT ");

    for (int i = 0; i < program->instruction_count; i++) {
        vdbe_instruction_t *instr = &program->instructions[i];
        const char *instr_sql = vdbe_opcode_to_sql(instr->opcode, instr->p1, instr->p2, instr->p3);

        size_t current_len = strlen(sql_buffer);
        size_t remaining = buffer_size - current_len;

        if (i == program->instruction_count - 1) {
            // Last instruction
            snprintf(sql_buffer + current_len, remaining, "%s", instr_sql);
        } else {
            // Chain operations
            snprintf(sql_buffer + current_len, remaining, "%s, ", instr_sql);
        }
    }

    return 0;
}

// Compile VDBE program to SQLite statement
int vdbe_compile_to_sqlite(vdbe_program_t *program, sqlite3 *db, sqlite3_stmt **stmt) {
    if (!program || !db || !stmt) return -1;

    char sql[2048];
    if (vdbe_program_to_sql(program, sql, sizeof(sql)) != 0) {
        return -1;
    }

    printf("Compiling SQL: %s\n", sql);

    if (sqlite3_prepare_v2(db, sql, -1, stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "SQL compilation error: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    // Bind parameters if needed
    int param_count = sqlite3_bind_parameter_count(*stmt);
    for (int i = 1; i <= param_count; i++) {
        sqlite3_bind_null(*stmt, i);  // Default binding
    }

    return 0;
}

// Enhanced opcode emitters
int vdbe_emit_literal(vdbe_program_t *program, int value) {
    return vdbe_add_instruction(program, VDBE_INTEGER, value, 0, 0);
}

int vdbe_emit_arithmetic(vdbe_program_t *program, const char *operation) {
    if (strcmp(operation, "+") == 0) {
        return vdbe_add_instruction(program, VDBE_ADD, 0, 0, 0);
    } else if (strcmp(operation, "-") == 0) {
        return vdbe_add_instruction(program, VDBE_SUBTRACT, 0, 0, 0);
    } else if (strcmp(operation, "*") == 0) {
        return vdbe_add_instruction(program, VDBE_MULTIPLY, 0, 0, 0);
    } else if (strcmp(operation, "/") == 0) {
        return vdbe_add_instruction(program, VDBE_DIVIDE, 0, 0, 0);
    }
    return -1;
}

int vdbe_emit_io(vdbe_program_t *program, const char *operation) {
    if (strcmp(operation, ".") == 0) {
        return vdbe_add_instruction(program, VDBE_PRINT, 0, 0, 0);
    } else if (strcmp(operation, "emit") == 0) {
        return vdbe_add_instruction(program, VDBE_EMIT, 0, 0, 0);
    }
    return -1;
}

int vdbe_emit_stack_operation(vdbe_program_t *program, const char *operation) {
    if (strcmp(operation, "dup") == 0) {
        return vdbe_add_instruction(program, VDBE_DUP, 0, 0, 0);
    } else if (strcmp(operation, "drop") == 0) {
        // DROP doesn't emit SQL - it's handled by the VM
        return 0;
    } else if (strcmp(operation, "swap") == 0) {
        // SWAP is handled by parameter reordering
        return 0;
    } else if (strcmp(operation, "over") == 0) {
        // OVER is handled by parameter duplication
        return 0;
    }
    return -1;
}

// Execute a compiled VDBE program
int vdbe_execute_program(sqlite3_stmt *stmt, forth_vm_t *vm) {
    if (!stmt || !vm) return -1;

    int result = sqlite3_step(stmt);

    if (result == SQLITE_ROW) {
        int column_count = sqlite3_column_count(stmt);
        for (int i = 0; i < column_count; i++) {
            const char *text = (const char*)sqlite3_column_text(stmt, i);
            if (text) {
                printf("%s ", text);
            }
        }
        printf("\n");
    } else if (result == SQLITE_DONE) {
        // No output, which is fine
    } else {
        fprintf(stderr, "Execution error: %s\n", sqlite3_errmsg(sqlite3_db_handle(stmt)));
        return -1;
    }

    sqlite3_reset(stmt);
    return 0;
}