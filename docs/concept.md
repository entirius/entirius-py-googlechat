---
title: Concept
description: Why an incoming webhook, what the client does and does not do, and where it sits in Entirius.
---

## The webhook model

A Google Chat **incoming webhook** is a URL bound to one space. An HTTP `POST` of a message body to that
URL creates a message in the space, posted by the webhook's name and avatar. There is no OAuth flow, no
service account and no bot user: authorisation is the `key` + `token` pair inside the URL. That makes the
URL itself the credential, and it is why the client treats it as a secret end to end.

The model is one-way. A webhook cannot read the space, receive replies or edit messages through this
library; it only posts.

## What the client does

- Builds the two message shapes Entirius needs: plain `text`, and a `cardsV2` card with a header, a text
  paragraph and at most one link button.
- Retries what can succeed on a second try — transport errors and 5xx — with exponential backoff, and
  gives up at once on 4xx, which a retry cannot fix (bad payload, revoked webhook, rate limit).
- Reports failure as one exception type, `GoogleChatError`, with the HTTP status or `None`.
- Keeps the URL out of logs and exceptions.

## What it does not do

- No queueing, persistence or deduplication — a retry after a timeout can post the same message twice if
  Google accepted the first request. Delivery bookkeeping belongs to the caller.
- No async API; calls block the thread for up to `max_retries` attempts plus the backoff sleeps.
- No threads, message updates, attachments or multi-section cards.
- No Django integration. The library is framework-free on purpose, so a Django module can depend on it
  optionally.

## In Entirius

`entirius-django-notifications` uses it for its chat channel: the notification module decides who is
notified and records the delivery; this library only performs the post. A missing package there means
chat deliveries are skipped, not failed.
