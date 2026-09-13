# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import json
import logging

import httpx
import pytest
import respx

from entirius_googlechat import GoogleChatError, GoogleChatWebhook

URL = "https://chat.googleapis.com/v1/spaces/AAA/messages?key=SECRETKEY&token=SECRETTOKEN"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr("entirius_googlechat.webhook.time.sleep", sleeps.append)
    return sleeps


def _sent(route) -> dict:
    return json.loads(route.calls.last.request.content)


@respx.mock
def test_send_text_payload():
    route = respx.post(URL).mock(return_value=httpx.Response(200, json={"name": "spaces/AAA/messages/1"}))
    assert GoogleChatWebhook(URL).send_text("hello") == "spaces/AAA/messages/1"
    assert _sent(route) == {"text": "hello"}


@respx.mock
def test_send_card_payload():
    route = respx.post(URL).mock(return_value=httpx.Response(200, json={"name": "m/2"}))
    GoogleChatWebhook(URL).send_card(
        title="T", text="body", subtitle="S", button_text="Open", button_url="https://x.test"
    )
    card = _sent(route)["cardsV2"][0]["card"]
    assert card["header"] == {"title": "T", "subtitle": "S"}
    widgets = card["sections"][0]["widgets"]
    assert widgets[0] == {"textParagraph": {"text": "body"}}
    assert widgets[1]["buttonList"]["buttons"][0]["onClick"]["openLink"]["url"] == "https://x.test"


@respx.mock
def test_send_card_without_button_has_one_widget():
    route = respx.post(URL).mock(return_value=httpx.Response(200, json={"name": "m/3"}))
    GoogleChatWebhook(URL).send_card(title="T", text="body")
    assert len(_sent(route)["cardsV2"][0]["card"]["sections"][0]["widgets"]) == 1


@respx.mock
def test_N03_5xx_retries_then_raises(no_sleep):
    route = respx.post(URL).mock(return_value=httpx.Response(503))
    with pytest.raises(GoogleChatError) as exc_info:
        GoogleChatWebhook(URL).send_text("x")
    assert route.call_count == 3
    assert exc_info.value.status_code == 503
    assert no_sleep == [1, 2]


@respx.mock
def test_transport_error_retried_then_succeeds():
    route = respx.post(URL).mock(side_effect=[httpx.ConnectError("boom"), httpx.Response(200, json={"name": "m/4"})])
    assert GoogleChatWebhook(URL).send_text("x") == "m/4"
    assert route.call_count == 2


@respx.mock
def test_4xx_no_retry():
    route = respx.post(URL).mock(return_value=httpx.Response(400))
    with pytest.raises(GoogleChatError) as exc_info:
        GoogleChatWebhook(URL).send_text("x")
    assert route.call_count == 1
    assert exc_info.value.status_code == 400


@respx.mock
def test_webhook_url_never_logged_or_in_error(caplog):
    caplog.set_level(logging.DEBUG)
    respx.post(URL).mock(side_effect=httpx.ConnectError(f"cannot reach {URL}"))
    with pytest.raises(GoogleChatError) as exc_info:
        GoogleChatWebhook(URL).send_text("x")
    rendered = f"{exc_info.value!s} {exc_info.value!r} {exc_info.value.__cause__!r} {caplog.text}"
    assert "SECRET" not in rendered
    assert exc_info.value.__cause__ is None
