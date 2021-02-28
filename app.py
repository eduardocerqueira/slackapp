import os
import re
import logging
from slack_bolt import App

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)

# Initializes app with credentials
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


# messages https://slack.dev/bolt-python/concepts#message-listening

@app.message("knock knock")
def ask_who(say):
    say("_Who's there?_")


@app.message(re.compile("(elf|ELF|Elf)"))
def say_hello_regex(say, context, logger, body):
    logger.info(body)
    greeting = context['matches'][0]
    say(f"Hi! {greeting} is here, how may I help you?")


# webAPI https://slack.dev/bolt-python/concepts#web-api
@app.message("wake me up")
def say_hello(client, message):
    channel_id = message["channel"]
    client.chat_postMessage(
        channel=channel_id,
        text="Summer has come and passed"
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


# The echo command simply echoes on command
@app.command("/test")
def repeat_text(ack, say, command):
    # Acknowledge command request
    ack()
    say(f"oi")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to your _App's Home_* :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Click me!"
                                }
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


# Start app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
