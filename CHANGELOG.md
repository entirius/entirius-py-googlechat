# Changelog

## 0.1.0 — unreleased

First release: a framework-free client for Google Chat incoming webhooks, used by the chat channel of
`entirius-django-notifications`.

- `GoogleChatWebhook(url, *, timeout=10.0, max_retries=3)` with `send_text(text)` and
  `send_card(*, title, text, subtitle, button_text, button_url)` (`cardsV2`, one section, optional link
  button); both return the created message `name`.
- Retries transport errors and 5xx with exponential backoff (1 s, 2 s, …); `max_retries` counts attempts in
  total; 4xx is raised at once. Covers edge case N-03.
- `GoogleChatError(status_code, message)` — `status_code` is `None` for transport errors.
- Any 2xx is success; the message `name` is parsed best-effort (`""` for a non-JSON or non-object body).
- The webhook URL (`key` + `token`) is never logged and never part of an exception: transport errors are
  re-raised without their cause, and building a client raises the `httpx` / `httpcore` loggers to `WARNING`.
- Docs: `api.md`, `install.md`, `concept.md`, `testing.md`, `gotchas.md`; `AGENTS.md` in the module shape.
