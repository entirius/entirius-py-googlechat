---
title: Install
description: Requirements, installing the package, obtaining a webhook URL and storing it.
---

## Requirements

| Requirement | Notes |
|---|---|
| Python ≥ 3.11 | |
| `httpx` ≥ 0.27 | the only runtime dependency |
| Outbound HTTPS to `chat.googleapis.com` | from the process that sends, typically a worker |

No Django, no settings module, no environment variables — the caller passes the URL.

## Install

```shell
pip install entirius-py-googlechat
# or, in a uv project
uv add entirius-py-googlechat
```

Django hosts usually get it through an extra of the consumer, e.g.
`entirius-django-notifications[googlechat]`; the consumer soft-imports `entirius_googlechat` and skips
chat deliveries when it is absent.

## Webhook URL

1. In Google Chat, open the space → *Apps & integrations* → *Webhooks* → add a webhook.
2. Copy the URL: `https://chat.googleapis.com/v1/spaces/<space>/messages?key=<key>&token=<token>`.
3. Store it where the host keeps secrets (environment, secret manager, an encrypted settings row) — never in
   the repository, a fixture or a log line. Anyone holding the URL can post to the space.

Revoking the webhook in the space settings invalidates the URL; the client then receives a 4xx, which is
not retried (`api.md` § Retries).

## Smoke check

```python
from entirius_googlechat import GoogleChatWebhook

GoogleChatWebhook(url).send_text("entirius-py-googlechat smoke test")
```

A returned `spaces/…/messages/…` name means the space received the message.
