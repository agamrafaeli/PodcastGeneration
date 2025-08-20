#!/bin/bash
# test-runner.sh - Smart test execution script for different development contexts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${BLUE}TTS Test Runner - Smart test execution for different contexts${NC}"
    echo -e "${YELLOW}Usage:${NC} ./test-runner.sh [OPTION]"
    echo ""
    echo -e "${CYAN}Speed-based options:${NC}"
    echo "  fast      - Ultra-fast development tests (mocks, no slow tests) ~5s"
    echo "  slow      - Only slow tests (real engines, file I/O) ~15s"  
    echo "  full      - All tests with comprehensive timing ~12s"
    echo ""
    echo -e "${CYAN}Category-based options:${NC}"
    echo "  unit      - Isolated unit tests (mocked)"
    echo "  integration - Cross-component integration tests"  
    echo "  e2e       - End-to-end workflow tests"
    echo "  real      - Force real TTS engines (slow but authentic)"
    echo ""
    echo -e "${CYAN}Development workflows:${NC}"
    echo "  dev       - Quick development cycle (fast tests)"
    echo "  check     - Pre-commit verification (integration tests)"
    echo "  ci        - CI/CD mode (all tests, real engines, parallel)"
    echo ""
    echo -e "${CYAN}Advanced options:${NC}"
    echo "  parallel  - Run tests in parallel (requires pytest-xdist)"
    echo "  debug     - Run with detailed output and no capture"
    echo "  timing    - Show detailed timing information"
    echo ""
}

run_tests() {
    local mode=$1
    local start_time=$(date +%s)
    
    case $mode in
        "fast"|"dev")
            echo -e "${GREEN}🚀 Running fast development tests...${NC}"
            pytest tests/ -m "not slow" -v
            ;;
        "slow")
            echo -e "${YELLOW}🐌 Running slow tests only...${NC}" 
            pytest tests/ -m "slow" -v
            ;;
        "unit")
            echo -e "${PURPLE}🧩 Running unit tests...${NC}"
            pytest tests/ -m "unit" -v
            ;;
        "integration"|"check") 
            echo -e "${CYAN}🔗 Running integration tests...${NC}"
            pytest tests/ -m "integration" -v
            ;;
        "e2e")
            echo -e "${BLUE}🎯 Running end-to-end tests...${NC}"
            pytest tests/ -m "e2e" -v
            ;;
        "real")
            echo -e "${RED}🎤 Running with REAL TTS engines (slow)...${NC}"
            TEST_MODE=real pytest tests/ -v
            ;;
        "full")
            echo -e "${GREEN}📊 Running full test suite with timing...${NC}"
            pytest tests/ -v --durations=0
            ;;
        "parallel")
            echo -e "${GREEN}⚡ Running tests in parallel (auto-detect cores)...${NC}"
            if ! pytest --version | grep -q "xdist"; then
                echo -e "${YELLOW}Installing pytest-xdist for parallel execution...${NC}"
                pip install pytest-xdist
            fi
            pytest tests/ -m "not slow" -n auto -v
            ;;
        "parallel-full")
            echo -e "${GREEN}⚡ Running ALL tests in parallel...${NC}"
            if ! pytest --version | grep -q "xdist"; then
                echo -e "${YELLOW}Installing pytest-xdist for parallel execution...${NC}"
                pip install pytest-xdist
            fi
            pytest tests/ -n auto -v --durations=10
            ;;
        "performance")
            echo -e "${CYAN}📊 Performance comparison: serial vs parallel...${NC}"
            echo -e "${BLUE}🔄 Serial execution:${NC}"
            time pytest tests/ -m "not slow" -v --tb=no -q
            echo -e "\n${GREEN}⚡ Parallel execution:${NC}"
            time pytest tests/ -m "not slow" -n auto -v --tb=no -q
            ;;
        "ci")
            echo -e "${PURPLE}🏗️ CI/CD mode: All tests, real engines, parallel...${NC}"
            TEST_MODE=real pytest tests/ -n auto -v --durations=10
            ;;
        "debug")
            echo -e "${RED}🐛 Debug mode: Detailed output, no capture...${NC}"
            pytest tests/ -v -s --tb=long
            ;;
        "timing")
            echo -e "${CYAN}⏱️ Detailed timing analysis...${NC}"
            pytest tests/ -v --durations=0 --durations-min=0.1
            ;;
        *)
            echo -e "${RED}Unknown option: $mode${NC}"
            show_help
            exit 1
            ;;
    esac
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo -e "${GREEN}✅ Tests completed in ${duration} seconds${NC}"
}

# Main execution
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}No option provided. Running fast development tests...${NC}"
    run_tests "fast"
elif [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
else
    run_tests "$1"
fi
