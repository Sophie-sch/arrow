# AGENTS.md

Arrow is the PyPI `arrow` package ("better dates & times", arrow-py/arrow) — **not** Apache Arrow. Build backend is flit_core; `arrow/_version.py` is the single version source (pyproject.toml declares `dynamic = ["version"]`).

## Commands

- Test everything: `pytest` (default addopts in `tox.ini` enforce branch coverage `--cov-fail-under=99`). The suite **fails below 99% coverage**, so new code needs matching tests. For a fast focused loop, bypass the coverage gate with `pytest --no-cov tests/test_xxx.py`.
- Lint: `pre-commit run --all-files --show-diff-on-failure` (CI runs `tox -e lint`). Black 88-col, isort, flake8, mypy-strict, pyupgrade all enforced here — CI will reject non-Black formatting.
- Docs: `tox -e docs` (doc8 + sphinx built with `-W --keep-going`; Sphinx warnings fail the build).
- CI matrix runs tox across 3.8–3.13 + pypy3 on ubuntu/macos/windows; don't use features newer than 3.8 (though pre-commit runs pyupgrade with `--py36-plus`).

## Environment gotchas

- `Makefile` targets (`make test`, `make lint`, `make docs`) assume a POSIX shell and `venv/bin/activate`. On Windows, run `pytest` / pre-commit directly — the Makefile recipes will not work.
- Setup a dev env with `pip install -r requirements/requirements-tests.txt`. `requirements/` files are sorted by the `requirements-txt-fixer` pre-commit hook.
- Timezone tests rely on `zoneinfo` (backported below 3.9) plus `tzdata`; they assume deterministic timezones, not the system local tz.

## Structure & style conventions

- Main package in `arrow/`; maintainers use `test.py` as a gitignored scratch file for debugging — safe to create and leave untracked.
- pytest config, coverage threshold, and style ignores live in `tox.ini`; mypy strict config in `setup.cfg` (tests are excluded from mypy).
- `arrow/locales.py` holds all locale strings (months, weekdays, humanization, `get_locale_by_class_name`). Locale tests in `tests/test_locales.py` **must** be classes named `Test<LocaleName>` (e.g. `TestEnglishLocale`) so the class-scoped `lang_locale` fixture can derive the locale name from `request.cls.__name__[4:]`.
- `tests/conftest.py` class-scoped fixtures store objects on `request.cls` (e.g. `self.arrow`, `self.datetime`) — test methods read them from `self`, not from direct fixture injection.