# AGENTS.md

Google Chat webhook client: text and card messages with retries — distribution `entirius-py-googlechat`, import `entirius_googlechat`.

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the import package `entirius_googlechat` — it is a public API contract.
- Default: do not commit — git is the user's call.

## Commit Message Format

**NEVER add `Co-Authored-By: Claude ...` (or any other Claude/Anthropic attribution) to commit messages.**

This overrides the default Claude Code behavior of appending a `Co-Authored-By` trailer. Commit messages MUST contain only the user's authored content — no robot footer, no "Generated with Claude Code" line, no co-author trailer.

Same rule applies to PR descriptions: no `Generated with [Claude Code]` footer.

## Architecture

- `webhook.py` — `GoogleChatWebhook(url, *, timeout=10.0, max_retries=3)`: `send_text(text) -> str` posts
  `{"text": ...}`; `send_card(*, title, text, subtitle="", button_text="", button_url="") -> str` posts `cardsV2`
  with one section and an optional button. Both return the created message `name`.
- Retries: transport errors and 5xx, backoff 1, 2, 4 s, `max_retries` attempts in total; 4xx never retried.
- `errors.py` — `GoogleChatError(status_code, message)`; `status_code` is `None` for transport errors.
- The webhook URL carries `key` + `token` — it is a secret. It is never logged and never put into an exception
  message; transport exceptions are re-raised without their cause (httpx messages can embed the URL).
- No Django dependency; consumers (e.g. `entirius-django-notifications`) soft-import it.
