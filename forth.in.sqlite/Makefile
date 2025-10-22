CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g -O2
LIBS = -lsqlite3
INCLUDES = -I/usr/include

SRCDIR = src
OBJDIR = obj
BINDIR = bin

SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(SOURCES:$(SRCDIR)/%.c=$(OBJDIR)/%.o)
TARGET = $(BINDIR)/forth-sqlite

all: $(TARGET)

$(TARGET): $(OBJECTS) | $(BINDIR)
	$(CC) $(OBJECTS) $(LIBS) -o $@

$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(OBJDIR):
	mkdir -p $(OBJDIR)

$(BINDIR):
	mkdir -p $(BINDIR)

demo: $(TARGET)
	./$(TARGET) demo.fth

test: $(TARGET)
	./$(TARGET) test.fth

clean:
	rm -rf $(OBJDIR) $(BINDIR)

.PHONY: all demo test clean