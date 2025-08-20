# Makefile for TTS test execution with different speed/completeness levels
.PHONY: help test test-fast test-slow test-unit test-integration test-e2e test-real test-full

help: ## Show this help message
	@echo "TTS Test Suite Commands:"
	@echo "========================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

test: ## Run fast development tests (mocks, excludes slow tests) - ~5s
	pytest tests/ -m "not slow" -v

test-fast: ## Same as 'test' - fast development testing
	pytest tests/ -m "not slow" -v

test-slow: ## Run only the slow tests (real engines, I/O intensive) 
	pytest tests/ -m "slow" -v

test-unit: ## Run only unit tests (isolated, mocked components)
	pytest tests/ -m "unit" -v

test-integration: ## Run integration tests (cross-component, can use mocks or real engines)
	pytest tests/ -m "integration" -v

test-e2e: ## Run end-to-end tests (full workflow validation)
	pytest tests/ -m "e2e" -v

test-real: ## Force all tests to use real engines (slow but comprehensive)
	TEST_MODE=real pytest tests/ -v

test-full: ## Run all tests with timing information
	pytest tests/ -v --durations=0

# Advanced test combinations - Phase 3: Parallel Execution
test-fast-parallel: ## Run fast tests in parallel (auto-detect CPU cores)
	pytest tests/ -m "not slow" -n auto -v

test-parallel: ## Run all tests in parallel (auto-detect CPU cores)
	pytest tests/ -n auto -v --durations=10

test-parallel-2: ## Run tests with 2 parallel workers
	pytest tests/ -n 2 -v

test-parallel-4: ## Run tests with 4 parallel workers
	pytest tests/ -n 4 -v

test-ci: ## CI/CD pipeline testing (all tests, real engines, parallel)
	TEST_MODE=real pytest tests/ -n auto -v --durations=10

# Performance testing
test-performance: ## Compare serial vs parallel execution performance
	@echo "🔄 Running serial execution..."
	@time pytest tests/ -m "not slow" -v --tb=no -q | head -20
	@echo "\n⚡ Running parallel execution..."
	@time pytest tests/ -m "not slow" -n auto -v --tb=no -q | head -20

# Development workflow shortcuts  
dev: test-fast ## Quick development cycle - fast tests only
check: test-integration ## Check integration points work
verify: test-full ## Full verification before commit

# Cleanup
clean: ## Clean test artifacts and temporary files
	rm -rf .pytest_cache/
	rm -rf generated/
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	find . -name "*.tmp" -delete
	find . -name "*.temp" -delete
	rm -f =*  # Clean any accidental pip installation log files
