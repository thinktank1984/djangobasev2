#include "forth.h"
#include "compiler.h"

// Interactive REPL
void repl(forth_vm_t *vm, forth_compiler_t *compiler) {
    printf("Forth-in-SQLite REPL\n");
    printf("Type 'help' for commands, 'quit' to exit\n\n");

    char line[MAX_INPUT_LEN];
    while (printf("forth> "), fflush(stdout), fgets(line, sizeof(line), stdin)) {
        // Remove trailing newline
        line[strcspn(line, "\n")] = '\0';

        if (strlen(line) == 0) {
            continue;
        }

        if (strcmp(line, "quit") == 0 || strcmp(line, "exit") == 0) {
            break;
        } else if (strcmp(line, "help") == 0) {
            printf("Commands:\n");
            printf("  : name ... ;  - Define a new word\n");
            printf("  .s            - Show stack contents\n");
            printf("  words         - List all defined words\n");
            printf("  help          - Show this help\n");
            printf("  quit          - Exit the REPL\n");
            printf("\nPrimitives: + - * / dup drop swap over . emit\n");
        } else if (strcmp(line, ".s") == 0) {
            printf("<%d> ", stack_depth(vm));
            for (int i = vm->stack_ptr - 1; i >= 0; i--) {
                printf("%d ", vm->data_stack[i]);
            }
            printf("\n");
        } else if (strcmp(line, "words") == 0) {
            printf("Dictionary:\n");
            for (int i = 0; i < vm->dict_size; i++) {
                forth_word_t *word = &vm->dictionary[i];
                const char *type = (word->type == WORD_PRIMITIVE) ? "prim" :
                                 (word->type == WORD_COMPILED) ? "comp" : "imm";
                printf("  %s (%s)\n", word->name, type);
            }
        } else if (strcmp(line, "compile") == 0) {
            printf("Entering compilation mode\n");
            // In a full implementation, this would switch to compilation mode
        } else {
            // Process the line
            if (compiler->state == COMPILER_COMPILING) {
                // We're compiling a word definition
                if (compiler_compile_token(compiler, line) != 0) {
                    fprintf(stderr, "Compilation error\n");
                }
            } else {
                // Check if it's a word definition
                if (strncmp(line, ": ", 2) == 0) {
                    // Start word definition
                    char *word_start = line + 2;
                    char *word_end = strtok(word_start, " ");
                    if (word_end) {
                        compiler_start_word(compiler, word_end);
                    }
                } else {
                    // Execute immediately
                    if (forth_execute(vm, line) != 0) {
                        fprintf(stderr, "Execution error\n");
                    }
                }
            }
        }
    }
}

// File execution
int execute_file(forth_vm_t *vm, forth_compiler_t *compiler, const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Failed to open file");
        return -1;
    }

    printf("Executing file: %s\n", filename);

    char line[MAX_INPUT_LEN];
    int line_number = 0;

    while (fgets(line, sizeof(line), file)) {
        line_number++;

        // Remove trailing newline
        line[strcspn(line, "\n")] = '\0';

        // Skip empty lines and comments
        if (strlen(line) == 0 || line[0] == '\\') {
            continue;
        }

        printf("%d: %s\n", line_number, line);

        // Process the line
        if (compiler->state == COMPILER_COMPILING) {
            if (compiler_compile_token(compiler, line) != 0) {
                fprintf(stderr, "Compilation error on line %d\n", line_number);
                fclose(file);
                return -1;
            }
        } else {
            if (strncmp(line, ": ", 2) == 0) {
                char *word_start = line + 2;
                char *word_end = strtok(word_start, " ");
                if (word_end) {
                    compiler_start_word(compiler, word_end);
                }
            } else {
                if (forth_execute(vm, line) != 0) {
                    fprintf(stderr, "Execution error on line %d\n", line_number);
                    fclose(file);
                    return -1;
                }
            }
        }
    }

    fclose(file);
    return 0;
}

int main(int argc, char *argv[]) {
    forth_vm_t vm;
    forth_compiler_t compiler;

    // Initialize VM
    const char *db_path = "forth.db";
    if (forth_init(&vm, db_path) != 0) {
        fprintf(stderr, "Failed to initialize Forth VM\n");
        return 1;
    }

    // Initialize compiler
    if (compiler_init(&compiler, &vm) != 0) {
        fprintf(stderr, "Failed to initialize Forth compiler\n");
        forth_cleanup(&vm);
        return 1;
    }

    // Load previously compiled words
    compiler_load_all_words(&compiler);

    printf("Forth-in-SQLite initialized with database: %s\n", db_path);
    printf("Loaded %d words from dictionary\n", vm.dict_size);

    if (argc == 1) {
        // Interactive mode
        repl(&vm, &compiler);
    } else if (argc == 2) {
        // File execution mode
        if (execute_file(&vm, &compiler, argv[1]) == 0) {
            printf("File executed successfully\n");
        } else {
            fprintf(stderr, "File execution failed\n");
        }
    } else {
        fprintf(stderr, "Usage: %s [filename.fth]\n", argv[0]);
    }

    // Cleanup
    compiler_cleanup(&compiler);
    forth_cleanup(&vm);

    return 0;
}