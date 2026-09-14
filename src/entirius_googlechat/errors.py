# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Errors raised by the Google Chat client."""


class GoogleChatError(Exception):
    """A webhook call failed. Never carries the webhook URL (it holds `key` and `token`)."""

    def __init__(self, status_code: int | None, message: str) -> None:
        super().__init__(f"Google Chat webhook failed (status={status_code}): {message}")
        self.status_code = status_code
        self.message = message
