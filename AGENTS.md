# AGENTS.md

entirius-py-googlechat — Google Chat incoming-webhook client: text and card messages with retries.
Distribution `entirius-py-googlechat`, import `entirius_googlechat`. Plain Python library, no Django.

## Quick Reference

- Python ≥ 3.11, `httpx`, `uv`, ruff, hatchling, pytest + respx, MPL-2.0.
- Read first: `docs/install.md` (host) · `docs/api.md` (caller) · `docs/concept.md` (why) ·
  `docs/gotchas.md` (before editing). This file is the map; it explains nothing twice.

## Commands

| Command | Meaning |
|---|---|
| `make install` | `uv sync --all-extras` |
| `make test` | pytest — no database, no network (respx) |
| `make check` / `fix` | ruff lint + format (+ canonical `.gitleaks.toml` guard) |

## Conventions

- English only; MPL-2.0 header on every `.py` (`insert-license`); no Claude/Anthropic attribution in
  commits or PRs.
- Public API = `GoogleChatWebhook`, `GoogleChatError` (`__init__.py` `__all__`). Never rename the import
  package `entirius_googlechat`.
- Framework-free: no Django import, no settings, no env reads — the caller passes the URL.
- Git flow: `develop` + `master`, PRs, semver tag on `master`. Do not commit by default — the operator decides.

## Map

```
src/entirius_googlechat/
├── __init__.py   public exports, __version__
├── webhook.py    GoogleChatWebhook: send_text, send_card → _post (retry loop) → _attempt (one httpx.post)
└── errors.py     GoogleChatError(status_code | None, message)
tests/test_webhook.py
```

## Where things live

| Question | Answer |
|---|---|
| Method signatures, payload shapes, return value | `docs/api.md` |
| Retry policy, backoff, what is final | `docs/api.md` § Retries; `webhook.py` `_retryable` |
| Why a webhook, what the client does not do | `docs/concept.md` |
| Secret handling, logging side effects | `docs/gotchas.md` |
| Which test covers what | `docs/testing.md` |
| What changed and why | `CHANGELOG.md` |

## Testing

- `respx` intercepts every request; an autouse fixture records `time.sleep` delays instead of sleeping.
- Tests use a URL with `SECRETKEY` / `SECRETTOKEN` and assert those strings never reach logs or exceptions —
  every new error path keeps that assertion.

## Testing end-to-end

- Edge cases covered here: N-03 (webhook 5xx retried, then raised — `test_N03_5xx_retries_then_raises`).
- No one-shot tags; the library has no BDD scenarios of its own — chat delivery is exercised through
  `entirius-django-notifications`.
- Guides: portal `guides/leads-end-to-end-testing.md`; emporium test package `docs/e2e-leads-funnel.md`.

## Gotchas

`docs/gotchas.md` — the only list. Read it before touching logging, exceptions or the retry loop.
