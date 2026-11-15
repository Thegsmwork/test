"""Temporary Telegram bot for the Hosting app deployment test."""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or "8186037303:AAEZw0Po5Nf61kfYlPE8OWsOrdHJsZWRSK0"


def telegram(method, **params):
    request = Request(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        data=json.dumps(params).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=35) as response:
        return json.load(response)["result"]


def main():
    bot = telegram("getMe")
    print(f"Hosting test bot ready: @{bot['username']}", flush=True)
    offset = 0
    while True:
        try:
            updates = telegram(
                "getUpdates", offset=offset, timeout=25, allowed_updates=["message"]
            )
            for update in updates:
                message = update.get("message", {})
                text = message.get("text", "")
                command = text.split(maxsplit=1)[0].split("@", 1)[0] if text else ""
                if message.get("chat", {}).get("type") == "private" and command in {"/start", "/ping"}:
                    telegram(
                        "sendMessage",
                        chat_id=message["chat"]["id"],
                        text="Hosting test bot is online." if command == "/start" else "pong",
                    )
                    print(f"Handled {command}", flush=True)
                offset = update["update_id"] + 1
        except HTTPError as error:
            print(f"Telegram API HTTP {error.code}; retrying.", flush=True)
            time.sleep(5)
        except (URLError, TimeoutError):
            print("Telegram connection interrupted; retrying.", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        raise SystemExit(f"Telegram startup failed (HTTP {error.code}).") from None
    except (URLError, TimeoutError):
        raise SystemExit("Telegram startup connection failed.") from None

