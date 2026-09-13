# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Incoming-webhook client for Google Chat spaces."""

import logging
import time
from typing import Any

import httpx

from entirius_googlechat.errors import GoogleChatError

logger = logging.getLogger(__name__)

# httpx/httpcore log the full request URL at INFO/DEBUG; the webhook URL holds `key` + `token`.
_URL_LOGGING_LIBRARIES = ("httpx", "httpcore")


class GoogleChatWebhook:
    """Posts messages to one Google Chat incoming webhook.

    Retries transport errors and 5xx with backoff 1, 2, 4 s; never retries 4xx.
    The URL is a secret and is never logged nor put into an exception message.
    """

    def __init__(self, url: str, *, timeout: float = 10.0, max_retries: int = 3) -> None:
        self._url = url
        self._timeout = timeout
        self._max_retries = max(1, max_retries)
        for name in _URL_LOGGING_LIBRARIES:
            logging.getLogger(name).setLevel(logging.WARNING)

    def send_text(self, text: str) -> str:
        """Send a plain-text message; returns the created message `name`."""
        return self._post({"text": text})

    def send_card(
        self, *, title: str, text: str, subtitle: str = "", button_text: str = "", button_url: str = ""
    ) -> str:
        """Send a `cardsV2` message with one section and an optional button; returns the message `name`."""
        widgets: list[dict[str, Any]] = [{"textParagraph": {"text": text}}]
        if button_text and button_url:
            button = {"text": button_text, "onClick": {"openLink": {"url": button_url}}}
            widgets.append({"buttonList": {"buttons": [button]}})
        card = {"header": {"title": title, "subtitle": subtitle}, "sections": [{"widgets": widgets}]}
        return self._post({"cardsV2": [{"cardId": "entirius", "card": card}]})

    def _post(self, payload: dict[str, Any]) -> str:
        for attempt in range(self._max_retries):
            try:
                return self._attempt(payload)
            except GoogleChatError as exc:
                if not self._retryable(exc) or attempt == self._max_retries - 1:
                    raise
                logger.warning("Google Chat attempt %d failed: %s", attempt + 1, exc)
                time.sleep(2**attempt)
        raise AssertionError("unreachable")

    def _attempt(self, payload: dict[str, Any]) -> str:
        try:
            response = httpx.post(self._url, json=payload, timeout=self._timeout)
        except httpx.TransportError as exc:
            raise GoogleChatError(None, type(exc).__name__) from None
        if response.status_code >= 400:
            raise GoogleChatError(response.status_code, response.reason_phrase)
        return self._message_name(response)

    @staticmethod
    def _message_name(response: httpx.Response) -> str:
        """Best-effort `name` from a 2xx body; a non-JSON or non-object body is still a successful post."""
        try:
            return response.json().get("name", "")
        except (ValueError, AttributeError):
            return ""

    @staticmethod
    def _retryable(exc: GoogleChatError) -> bool:
        return exc.status_code is None or exc.status_code >= 500
