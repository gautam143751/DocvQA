# Repository Guidelines

## Project Structure & Module Organization
The repository currently contains only `README.md`; add application code under `src/docvqa/` using subpackages such as `models/`, `data/`, and `evaluation/`. Place reusable scripts in `scripts/` (name them with verbs, e.g., `prepare_dataset.py`) and keep exploratory work in `notebooks/` with numbered prefixes (`01_data_audit.ipynb`). Store small sample documents in `assets/samples/` and keep large datasets out of version control; document their locations in `docs/datasets.md`.

## Build, Test, and Development Commands
Create an isolated environment (`python -m venv .venv && source .venv/bin/activate`) and install dependencies with `pip install -r requirements.txt` once introduced. Run the package in editable mode (`pip install -e .`) to enable local module imports. Execute unit tests with `pytest` and measure coverage via `pytest --cov=docvqa`. Use `pre-commit run --all-files` before pushing to ensure formatters and linters pass.

## Coding Style & Naming Conventions
Prefer Python 3.10+. Follow PEP 8 with 4-space indentation and limit lines to 100 characters. Use snake_case for functions and variables, PascalCase for classes, and verbs for command-line scripts. Apply `black` and `isort` for formatting, and configure `ruff` or `flake8` for linting; keep configuration in `pyproject.toml`. Type annotations are expected for public functions, and docstrings should follow the Google style.

## Testing Guidelines
Organize tests to mirror the package structure (`tests/models/test_reader.py` pairs with `src/docvqa/models/reader.py`). Name files `test_*.py`, and use descriptive test function names (`test_reader_handles_tesseract_errors`). Mock external OCR services and keep fixtures in `tests/fixtures/`. Aim for ≥85% statement coverage on critical modules; add regression tests for every bug fix and ensure `pytest -m slow` can be skipped locally.

## Commit & Pull Request Guidelines
The existing history uses short, Title Case summaries (e.g., `First Repo Commit`); keep commits concise, imperative, and scoped to one change. Reference GitHub issues in the body when relevant (`Refs #42`). Pull requests should include: a one-paragraph overview, a checklist of validation steps (tests, lint), screenshots or sample outputs for UI/model metric changes, and notes on data dependencies or new configuration files.

## Security & Configuration Tips
Never commit documents containing PII; store credentials in environment variables managed via `.env` and document required keys in `docs/configuration.md`. Validate third-party OCR models or embeddings through reproducible benchmarks, and review licenses before adding new datasets.
