---
title: Gotchas
description: The rules that bite — secret handling first, then retries and logging side effects.
---

Each item: the rule, then where it is enforced.

## The webhook URL is a secret

- **The `key` and `token` query parameters authorise posting.** Anyone with the URL can post to the space;
  treat it like a password in storage, configuration, fixtures and screenshots.
- **The URL is never logged.** The client's own warning logs the attempt number and the error text only
  (`webhook.py` `_post`). Test: `test_webhook_url_never_logged_at_info`.
- **The URL is never put into an exception.** `GoogleChatError` carries a status and a short message — the
  httpx exception class name or the HTTP reason phrase (`webhook.py` `_attempt`).
- **Transport errors are re-raised `from None`.** httpx exception messages can contain the request URL; a
  chained `__cause__` would surface it in any traceback. Test: `test_webhook_url_never_logged_or_in_error`.
  Never add `from exc` there.
- **Callers must not undo this.** Do not log the URL, `repr` an object holding it, or include it in an
  error raised on top of `GoogleChatError`. Store and display a masked form if an admin needs to recognise
  which webhook is configured.

## Logging

- **Building a client raises the `httpx` and `httpcore` loggers to `WARNING`, process-wide.** Both log the
  full request URL at INFO/DEBUG. A host that wants httpx request logs for other clients loses them once a
  `GoogleChatWebhook` exists; lowering those loggers again re-exposes the webhook secret. Test:
  `test_webhook_url_never_logged_at_info`.

## Retries

- **`max_retries` counts attempts, not retries.** The default 3 means one request plus two retries.
- **4xx is final, 429 included.** Google Chat rate-limits posts per space; the client does not back off on
  429 — throttle on the caller's side.
- **Backoff sleeps block the calling thread** (1 s, 2 s, … between attempts). Send from a worker.
- **A retried timeout can duplicate a message.** If Google accepted a request whose response never arrived,
  the retry posts again. The client has no idempotency key.

## Responses

- **Any 2xx is success, and the returned `name` may be `""`.** A non-JSON or non-object body still means
  the message was posted; do not treat an empty name as a failure.
