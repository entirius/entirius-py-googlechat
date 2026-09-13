# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Google Chat webhook client: text and card messages with retries"""

from entirius_googlechat.errors import GoogleChatError
from entirius_googlechat.webhook import GoogleChatWebhook

__version__ = "0.1.0"
__all__ = ["GoogleChatError", "GoogleChatWebhook"]
