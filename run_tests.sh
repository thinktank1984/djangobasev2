#!/bin/bash

# Django Blog Test Runner
# Runs tests for the Django blog application

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Default values
VERBOSE=false
COVERAGE=true  # Coverage is ON by default
TEST_MODE="all"  # Default to running all tests
STOP_ON_FAILURE=false
TEST_PATTERN=""
SHOW_DURATIONS=false
DJANGO_TEST_ARGS=""
USE_VENV=true  # Use virtual environment by default

# Show help
show_help() {
    echo "Usage: ./run_tests.sh [OPTIONS]"
    echo ""
    echo "Test Selection:"
    echo "  --all              Run all tests [DEFAULT]"
    echo "  --app              Run only application tests"
    echo "  --specific APP     Run tests for specific Django app (e.g., --specific accounts)"
    echo "  -k PATTERN         Run tests matching PATTERN (e.g., -k test_model)"
    echo ""
    echo "Output Options:"
    echo "  -v, --verbose      Verbose output (show individual test names)"
    echo "  -vv                Very verbose output (show test details)"
    echo "  -x, --stop         Stop on first failure"
    echo "  --parallel         Run tests in parallel"
    echo "  --keepdb           Keep test database between runs"
    echo ""
    echo "Coverage Options:"
    echo "  --no-coverage      Skip coverage report (coverage enabled by default)"
    echo "  --cov-min=N        Fail if coverage below N% (default: no minimum)"
    echo ""
    echo "Environment Options:"
    echo "  --no-venv          Don't use virtual environment"
    echo "  --debug            Run with Django debug settings"
    echo ""
    echo "Other Options:"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh                          # Run all tests with coverage"
    echo "  ./run_tests.sh --app                    # Run application tests only"
    echo "  ./run_tests.sh -v --specific accounts   # Run accounts app tests verbosely"
    echo "  ./run_tests.sh -k test_model            # Run model-related tests"
    echo "  ./run_tests.sh -x --parallel            # Run in parallel, stop on first failure"
    echo "  ./run_tests.sh --no-coverage --app      # Run without coverage"
    echo "  ./run_tests.sh --keepdb                 # Keep test database for faster runs"
    echo "  ./run_tests.sh --debug                  # Run with debug settings"
    echo ""
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            if [ "$VERBOSE" = "false" ]; then
                VERBOSE=true
            else
                VERBOSE="vv"  # Very verbose if -v used twice
            fi
            shift
            ;;
        -vv)
            VERBOSE="vv"
            shift
            ;;
        -x|--stop)
            STOP_ON_FAILURE=true
            shift
            ;;
        -k)
            TEST_PATTERN="$2"
            shift 2
            ;;
        --specific)
            SPECIFIC_APP="$2"
            TEST_MODE="specific"
            shift 2
            ;;
        --parallel)
            DJANGO_TEST_ARGS="$DJANGO_TEST_ARGS --parallel"
            shift
            ;;
        --keepdb)
            DJANGO_TEST_ARGS="$DJANGO_TEST_ARGS --keepdb"
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --no-venv)
            USE_VENV=false
            shift
            ;;
        --debug)
            DJANGO_TEST_ARGS="$DJANGO_TEST_ARGS --debug-mode"
            shift
            ;;
        --all)
            TEST_MODE="all"
            shift
            ;;
        --app)
            TEST_MODE="app"
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧪 Django Blog Test Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Navigate to blogapp directory
cd blogapp

# Check if virtual environment should be used
if [ "$USE_VENV" = true ] && [ -d "../venv" ]; then
    echo -e "${GREEN}✅ Activating virtual environment...${NC}"
    source ../venv/bin/activate
elif [ "$USE_VENV" = true ]; then
    echo -e "${YELLOW}⚠️ Virtual environment not found, using system Python${NC}"
fi

# Check if Django project is set up correctly
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ manage.py not found. Please run this from the blogapp directory${NC}"
    exit 1
fi

# Check if requirements are installed
if ! python -c "import django" &> /dev/null; then
    echo -e "${RED}❌ Django not installed. Please install requirements first${NC}"
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}✅ Django environment ready${NC}"
echo ""

# Display test mode
case $TEST_MODE in
    all)
        echo -e "${CYAN}📋 Test Mode: ALL (All Django apps)${NC}"
        ;;
    app)
        echo -e "${CYAN}📋 Test Mode: Application Tests Only${NC}"
        ;;
    specific)
        echo -e "${CYAN}📋 Test Mode: Specific App: ${SPECIFIC_APP}${NC}"
        ;;
esac

# Display options
if [ -n "$TEST_PATTERN" ]; then
    echo -e "${CYAN}🔍 Test Pattern: $TEST_PATTERN${NC}"
fi
if [ "$VERBOSE" = "vv" ]; then
    echo -e "${CYAN}📢 Verbosity: Very Verbose (-vv)${NC}"
elif [ "$VERBOSE" = true ]; then
    echo -e "${CYAN}📢 Verbosity: Verbose (-v)${NC}"
fi
if [ "$STOP_ON_FAILURE" = true ]; then
    echo -e "${CYAN}⛔ Stop on first failure: Enabled${NC}"
fi
if [ "$COVERAGE" = false ]; then
    echo -e "${CYAN}📊 Coverage: Disabled${NC}"
fi
if [ "$USE_VENV" = false ]; then
    echo -e "${CYAN}🐍 Virtual Environment: Disabled${NC}"
fi

echo ""

# Build Django test command
TEST_CMD="python manage.py test"

# Add test target based on mode
case $TEST_MODE in
    all)
        # Test all Django apps
        TEST_CMD="$TEST_CMD ."
        ;;
    app)
        # Test all apps in the project
        TEST_CMD="$TEST_CMD ."
        ;;
    specific)
        # Test specific Django app
        if [ -z "$SPECIFIC_APP" ]; then
            echo -e "${RED}❌ Error: --specific requires an app name${NC}"
            exit 1
        fi
        TEST_CMD="$TEST_CMD $SPECIFIC_APP"
        ;;
esac

# Add test pattern
if [ -n "$TEST_PATTERN" ]; then
    TEST_CMD="$TEST_CMD -k $TEST_PATTERN"
fi

# Add verbosity
if [ "$VERBOSE" = "vv" ]; then
    TEST_CMD="$TEST_CMD --verbosity=2"
elif [ "$VERBOSE" = true ]; then
    TEST_CMD="$TEST_CMD --verbosity=1"
fi

# Add stop on failure
if [ "$STOP_ON_FAILURE" = true ]; then
    TEST_CMD="$TEST_CMD --failfast"
fi

# Add coverage if enabled
if [ "$COVERAGE" = true ]; then
    # Check if coverage is installed
    if ! python -c "import coverage" &> /dev/null; then
        echo -e "${YELLOW}⚠️ Coverage package not installed, installing...${NC}"
        pip install coverage
    fi
    TEST_CMD="coverage run --source='.' $TEST_CMD"
fi

# Add additional Django test arguments
if [ -n "$DJANGO_TEST_ARGS" ]; then
    TEST_CMD="$TEST_CMD $DJANGO_TEST_ARGS"
fi

echo -e "${CYAN}📝 Django Command: $TEST_CMD${NC}"
echo ""

TEST_FAILED=0

# Function to run Django tests
run_django_tests() {
    echo -e "${YELLOW}🔬 Running Django Tests...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if eval "$TEST_CMD"; then
        echo -e "${GREEN}✅ Django tests passed!${NC}"

        # Generate coverage report if coverage was enabled
        if [ "$COVERAGE" = true ]; then
            echo ""
            echo -e "${BLUE}📊 Generating coverage report...${NC}"
            coverage report
            coverage html
            echo -e "${GREEN}✅ Coverage report generated${NC}"
            echo -e "${BLUE}📊 HTML report available at: htmlcov/index.html${NC}"
        fi

        return 0
    else
        echo -e "${RED}❌ Django tests failed${NC}"
        return 1
    fi
}

# Run tests based on mode
case $TEST_MODE in
    all)
        run_django_tests || TEST_FAILED=1
        ;;
    app)
        run_django_tests || TEST_FAILED=1
        ;;
    specific)
        run_django_tests || TEST_FAILED=1
        ;;
    *)
        echo -e "${RED}Invalid test mode: $TEST_MODE${NC}"
        exit 1
        ;;
esac

# Final summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $TEST_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All Django tests passed!${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}📊 Coverage report generated at: blogapp/htmlcov/index.html${NC}"
        echo "   Open with: open blogapp/htmlcov/index.html"
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}❌ Some Django tests failed${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
