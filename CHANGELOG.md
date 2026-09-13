# Changelog

## 0.1.0 (unreleased)

- Scaffold from the Entirius module template.
- `GoogleChatWebhook` with `send_text` / `send_card`, retries on transport errors and 5xx, `GoogleChatError`;
  the webhook URL is never logged or included in errors.
