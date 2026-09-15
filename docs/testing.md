---
title: Testing
description: Running the suite, what each test covers, and how consumers test code that sends chat messages.
---

## Running

```shell
make install   # uv sync --all-extras
make test      # uv run pytest -x -q
```

No database, no network: every HTTP call is intercepted by `respx`. An autouse fixture replaces
`time.sleep` in `entirius_googlechat.webhook` and records the requested delays, so retry tests run instantly
and can assert the backoff.

## Test map (`tests/test_webhook.py`)

| Test | Covers |
|---|---|
| `test_send_text_payload` | `{"text": …}` body, returned message `name` |
| `test_send_card_payload` | `cardsV2` header, text paragraph, button with `openLink` |
| `test_send_card_without_button_has_one_widget` | no button unless both button fields are set |
| `test_N03_5xx_retries_then_raises` | edge case N-03: 3 attempts on 503, sleeps `[1, 2]`, `status_code` kept |
| `test_transport_error_retried_then_succeeds` | a transport error is retried, the next 2xx wins |
| `test_4xx_no_retry` | one request on 400, raised at once |
| `test_webhook_url_never_logged_or_in_error` | an httpx message embedding the URL leaks into neither the exception, its cause, nor the log |
| `test_webhook_url_never_logged_at_info` | httpx request logging stays silent at INFO after the client is built |
| `test_non_json_object_2xx_is_success` | HTML and JSON-list 2xx bodies return `""` |

Any test that touches the URL uses the fixture value with `SECRETKEY` / `SECRETTOKEN` and asserts those
strings are absent — keep that pattern for new error paths.

## Testing a consumer

Mock at the HTTP boundary with `respx` (as this suite does) or replace `GoogleChatWebhook` with a stub
in the consumer's tests. Never point a test at a real webhook: a test run would post to a real space and
the URL would end up in CI configuration.

## End-to-end

The library has no end-to-end suite of its own. Its behaviour in the leads platform is exercised through
`entirius-django-notifications`; see the portal guide `guides/leads-end-to-end-testing.md`.
