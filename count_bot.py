import os
import sys

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, SourceUser

channel_access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
channel_secret = os.environ["LINE_CHANNEL_SECRET"]

if channel_access_token is None or channel_secret is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)

app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    text_length = len(text)
    text_length_str = str(text_length)
    page = "1 page"
    if text_length > 400:
        page = str((text_length // 400) + 1) + " pages"
    if isinstance(event.source, SourceUser):
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="From: " + profile.display_name),
                TextSendMessage(text="Received message: " + text),
                TextSendMessage(text="Text length: " + text_length_str),
                TextSendMessage(text="400-character paper: " + page)
            ],
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="Received message: " + text),
                TextSendMessage(text="Text length: " + text_length_str),
                TextSendMessage(text="400-character manuscript paper: " + page)
            ]
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)