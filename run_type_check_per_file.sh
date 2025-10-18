#!/bin/bash
# Script to run type checking on each Python file individually
# and save results to separate output files - Django blog version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Output directory for results
OUTPUT_DIR="type_check_results"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}    Per-File Type Checking (Django)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Results will be saved to: $OUTPUT_DIR/${NC}"
echo ""

# Navigate to blogapp directory
cd blogapp

# Check if virtual environment exists
if [ -d "../venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source ../venv/bin/activate
fi

# Install mypy and Django stubs if not present
if ! python -c "import mypy" &> /dev/null; then
    echo -e "${YELLOW}Installing mypy and Django stubs...${NC}"
    pip install mypy django-stubs types-requests types-PyYAML
fi

# Counter
total_files=0
files_with_errors=0
files_clean=0

# Find all Python files in Django project (excluding migrations and cache)
echo -e "${BLUE}Finding Python files...${NC}"
python_files=$(find . -name "*.py" -type f ! -path "*/migrations/*" ! -path "*/__pycache__/*" ! -path "*/venv/*" ! -path "*/htmlcov/*" ! -path "*/screenshots/*" ! -path "*/static/*" ! -path "*/templates/*" 2>/dev/null)

total_count=$(echo "$python_files" | wc -l | tr -d ' ')
echo -e "${GREEN}Found $total_count Python files to check${NC}"
echo ""

# Process each file
current=0
for file in $python_files; do
    current=$((current + 1))
    total_files=$((total_files + 1))
    
    # Create output filename (replace / with _ and remove .py extension)
    output_file="$OUTPUT_DIR/$(echo $file | sed 's/\//_/g' | sed 's/\.py$//')_type_checking.txt"
    
    echo -e "${BLUE}[$current/$total_count]${NC} Checking: $file"
    
    # Run type check and save output
    if mypy --django-settings-module=core.settings --strict-optional --ignore-missing-imports "$file" > "$output_file" 2>&1; then
        # No errors
        files_clean=$((files_clean + 1))
        echo -e "  ${GREEN}✓ Clean${NC}"
    else
        # Has errors
        files_with_errors=$((files_with_errors + 1))
        # Count errors and warnings
        error_count=$(grep -c "error:" "$output_file" 2>/dev/null || echo "0")
        warning_count=$(grep -c "warning:" "$output_file" 2>/dev/null || echo "0")
        echo -e "  ${RED}✗ $error_count errors, $warning_count warnings${NC}"
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "  Total files: $total_files"
echo -e "  ${GREEN}Clean files: $files_clean${NC}"
echo -e "  ${RED}Files with issues: $files_with_errors${NC}"
echo ""
echo -e "Results saved to: ${BLUE}$OUTPUT_DIR/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create a summary file
summary_file="$OUTPUT_DIR/SUMMARY.txt"
echo "Type Checking Summary - $(date)" > "$summary_file"
echo "======================================" >> "$summary_file"
echo "" >> "$summary_file"
echo "Total files checked: $total_files" >> "$summary_file"
echo "Clean files: $files_clean" >> "$summary_file"
echo "Files with issues: $files_with_errors" >> "$summary_file"
echo "" >> "$summary_file"
echo "Files with errors or warnings:" >> "$summary_file"
echo "--------------------------------" >> "$summary_file"

# List files with issues
for result_file in "$OUTPUT_DIR"/*_type_checking.txt; do
    if grep -q "error:\|warning:" "$result_file" 2>/dev/null; then
        basename "$result_file" | sed 's/_type_checking\.txt$//' >> "$summary_file"
    fi
done

echo ""
echo -e "${GREEN}Summary saved to: $summary_file${NC}"
echo ""

exit 0

