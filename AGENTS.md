# Agent Guidelines

## General Good Practices
- Write clear, maintainable code with descriptive names and docstrings.
- Prefer small, focused functions and modules to enhance readability.
- Use `rg` for searching through the codebase; avoid `grep -R` or `ls -R`.
- Keep commits atomic and include meaningful messages.
- Document significant decisions and assumptions in code comments or Markdown files.

## Testing Philosophy
- Run `python -m pytest tests/ -v` before every commit to ensure the mock test suite passes.
- Add or update tests when introducing new features or fixing bugs.
- Favor mock tests during development for fast, deterministic feedback.
- Ensure tests avoid external network dependencies unless explicitly using real engine tests.
- When validating against real TTS engines, run `USE_REAL_ENGINES=true python -m pytest tests/ -v`.

## End-to-End Testing Strategy
- Treat the system as a black box by exercising only public CLI or SDK interfaces.
- Invoke workflows through subprocess calls (`python -m cli`, `tts-cli`, etc.) or SDK methods rather than importing internal modules.
- Keep scenarios self-contained with temporary files and assert outputs through observable artifacts like audio files or stdout.
- Mark these tests with `@pytest.mark.e2e` and run via `python -m pytest tests/ -m e2e -v` or `./test-runner.sh e2e`.
- Use mock engines by default; enable real engines explicitly when needed for full-stack verification.

## Module Structure Integrity
- Keep modules within `src/` organized by responsibility with clear `__init__.py` files.
- Avoid circular dependencies; refactor shared logic into common utilities when needed.
- Minimize side effects at import time; prefer explicit functions and classes.
- Use relative imports within the package to maintain module boundaries.
- Separate engine-specific code, shared utilities, and configuration into distinct modules to preserve clarity.
