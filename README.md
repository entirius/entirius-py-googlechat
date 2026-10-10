# entirius-py-googlechat

A Google Chat incoming-webhook client for Python, part of Entirius, the open-source modular ecommerce platform. It
posts text and card messages to one Chat space, retries transport errors and 5xx responses, and keeps the webhook URL
out of logs and exceptions.

[![PyPI](https://img.shields.io/pypi/v/entirius-py-googlechat.svg)](https://pypi.org/project/entirius-py-googlechat/)
[![Python](https://img.shields.io/pypi/pyversions/entirius-py-googlechat.svg)](https://pypi.org/project/entirius-py-googlechat/)
[![License: MPL-2.0](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://github.com/entirius/entirius-py-googlechat/blob/develop/LICENSE)

## What it does

- Posts a plain text message (`send_text()`).
- Posts a card with a title, a subtitle, a text and an optional link button (`send_card()`).
- Retries transport errors and 5xx responses with exponential backoff; a 4xx response is raised at once.
- Reports failure as one exception type, `GoogleChatError`, carrying the HTTP status or `None`.
- Never logs the webhook URL and never puts it into an exception.

## Installation

```shell
uv add entirius-py-googlechat
pip install entirius-py-googlechat
```

The import name is `entirius_googlechat`.

Requirements, obtaining the webhook URL and storing it:
https://github.com/entirius/entirius-py-googlechat/blob/develop/docs/install.md

## Quick start

```python
from entirius_googlechat import GoogleChatError, GoogleChatWebhook

url = "https://chat.googleapis.com/v1/spaces/<space>/messages?key=<key>&token=<token>"
try:
    name = GoogleChatWebhook(url).send_text("Deploy finished")
except GoogleChatError as exc:
    print(exc.status_code)
```

## Requirements

- Python 3.11 or newer.
- `httpx` (installed as a dependency).
- Outbound HTTPS to `chat.googleapis.com` and the incoming-webhook URL of a Chat space.

## Documentation

- Library documentation: https://github.com/entirius/entirius-py-googlechat/tree/develop/docs
- Entirius documentation: https://docs.entirius.com/
- Changelog: https://github.com/entirius/entirius-py-googlechat/blob/develop/CHANGELOG.md

## Part of Entirius

This library sends the chat notifications of the Entirius backend service (Volkanos) and its modules.

- Backend service: https://github.com/entirius/entirius-service-volkanos
- Docker harness: https://github.com/entirius/entirius-zeno
- Consumer module: https://github.com/entirius/entirius-django-notifications

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest); no database, no network
```

Development and agent instructions: https://github.com/entirius/entirius-py-googlechat/blob/develop/AGENTS.md

## License

Mozilla Public License 2.0 (MPL-2.0) — see https://github.com/entirius/entirius-py-googlechat/blob/develop/LICENSE.
