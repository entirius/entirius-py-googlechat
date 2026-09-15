---
title: Client API
description: GoogleChatWebhook and GoogleChatError — constructor, send methods, payloads, retries, errors.
---

The public API is two names, both exported from `entirius_googlechat`:
`GoogleChatWebhook` and `GoogleChatError`. Anything else in the package is internal.

```python
from entirius_googlechat import GoogleChatError, GoogleChatWebhook

chat = GoogleChatWebhook(webhook_url, timeout=10.0, max_retries=3)
try:
    name = chat.send_text("Deploy finished")
except GoogleChatError as exc:
    log.warning("chat delivery failed: status=%s", exc.status_code)
```

## `GoogleChatWebhook(url, *, timeout=10.0, max_retries=3)`

| Argument | Meaning |
|---|---|
| `url` | the incoming-webhook URL of one Chat space, including its `key` and `token` query parameters — a secret (`gotchas.md`) |
| `timeout` | seconds, passed to `httpx.post` for every attempt |
| `max_retries` | **attempts in total**, not retries after the first; values below 1 are treated as 1 |

The constructor makes no network call. It sets the `httpx` and `httpcore` loggers to `WARNING`
(`gotchas.md` § Logging). One instance can be reused for any number of messages; it holds no connection.

## `send_text(text) -> str`

Posts `{"text": text}`. Returns the created message `name` (`spaces/…/messages/…`).

## `send_card(*, title, text, subtitle="", button_text="", button_url="") -> str`

Posts one `cardsV2` card (`cardId` `"entirius"`): a header (`title`, `subtitle`), one section with a
`textParagraph` widget holding `text`, and — only when **both** `button_text` and `button_url` are
non-empty — a `buttonList` with one button that opens `button_url`. Returns the message `name`.

The library does not escape or truncate any field; the caller owns the content.

## Success

Any 2xx status is success. The message `name` is read from the JSON body best-effort: a non-JSON body or
a JSON value that is not an object returns `""`, never an error — the message was posted.

## Retries

| Outcome of an attempt | Retried |
|---|---|
| transport error (`httpx.TransportError`: connect, read, timeout, …) | yes |
| 5xx | yes |
| 4xx (including 429) | no — raised at once |

Between attempts the client sleeps `2 ** attempt` seconds (1, 2, 4, …) in the calling thread. With the default
`max_retries=3` a failing call makes 3 requests and sleeps 1 s + 2 s before raising. Each failed attempt that
will be retried logs one `WARNING` on `entirius_googlechat.webhook` (attempt number and the error text,
never the URL).

The call is synchronous and blocking: run it in a worker (Celery task, thread), not in a request handler.

## `GoogleChatError(status_code, message)`

The only exception the send methods raise for delivery failures.

| Attribute | Transport error | HTTP error |
|---|---|---|
| `status_code` | `None` | the HTTP status (`400`, `503`, …) |
| `message` | the httpx exception class name, e.g. `ConnectError` | the response reason phrase |

`str(exc)` is `Google Chat webhook failed (status=<status_code>): <message>`. A transport error is raised
`from None` — `__cause__` is empty, because httpx exception messages can embed the request URL.
